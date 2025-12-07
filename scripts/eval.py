# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the CC-by-NC license found in the
# LICENSE file in the root directory of this source tree.

import datetime
import os
import json  # [수정] 결과 저장을 위해 추가

import torch
import torch.distributed as dist

from data import data
from flow_matching.loss import MixturePathGeneralizedKL

from logic import evaluate, flow, generate

from torch.utils.data import DataLoader
from transformers import GPT2TokenizerFast
from utils import checkpointing


def run_eval(
    rank: int,
    seed: int,
    work_dir: str,
    batch_size: int,
    perplexity_n_samples: int,
    sampling_steps: int,
    eval_perplexity: bool,
    eval_elbo: bool,
    elbo_data: str,
    world_size: int,
    n_discretization: float = 1024,
) -> None:
    
    # [안전장치] 배치 사이즈 강제 1 고정 (OOM 방지)
    if batch_size != 1:
        if rank == 0:
            print(f"[Rank {rank}] Warning: Forcing batch_size to 1 (was {batch_size}) to prevent OOM.")
        batch_size = 1

    torch.manual_seed(seed + rank)

    # Logging and configuration
    work_dirs = checkpointing.get_work_dirs(work_dir=work_dir, rank=rank)

    device = torch.device(f"cuda:{rank}" if torch.cuda.is_available() else "cpu")

    cfg = checkpointing.load_cfg_from_path(work_dir=work_dirs.checkpoint)

    # Data
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    vocab_size = tokenizer.vocab_size

    # Flow matching
    path = flow.get_path(
        scheduler_type=cfg.flow.scheduler_type, exponent=cfg.flow.exponent
    )
    loss_fn = flow.get_loss_function(loss_function=cfg.flow.loss_function, path=path)
    # Elbo may have singularity at 1
    time_epsilon = 1e-3 if isinstance(loss_fn, MixturePathGeneralizedKL) else 0.0

    source_distribution = flow.get_source_distribution(
        source_distribution=cfg.flow.source_distribution, vocab_size=vocab_size
    )

    model = checkpointing.load_model_from_path(
        work_dir=work_dirs.checkpoint,
        device=device,
        source_distribution=source_distribution,
        cfg=cfg.model,
        vocab_size=vocab_size,
    )
    model.eval()

    if cfg.model.compile:
        model = torch.compile(model)
        torch.set_float32_matmul_precision("high")

    # [핵심] 추론 시 그래디언트 계산 끄기 (메모리 절약)
    with torch.no_grad():
        if eval_perplexity:
            assert perplexity_n_samples // batch_size > 0

            samples = []

            for _ in range(perplexity_n_samples // batch_size):
                generated = generate.generate_samples(
                    model=model,
                    step=0,
                    sample_dir=work_dirs.samples,
                    vocab_size=vocab_size,
                    tokenizer=tokenizer,
                    rank=rank,
                    device=device,
                    path=path,
                    source_distribution=source_distribution,
                    sample_batch_size=batch_size,
                    sequence_length=cfg.model.length,
                    sampling_steps=sampling_steps,
                    time_epsilon=time_epsilon,
                )
                # 생성된 샘플을 CPU로 옮겨서 GPU 메모리 누적 방지
                samples.append(generated.cpu())

            dist.barrier()
            
            # samples가 이미 CPU에 있으므로 cat도 CPU에서 수행
            samples = torch.cat(samples, dim=0)
            
            # 계산을 위해 GPU로 이동
            samples = samples.to(device)

            perplexity = evaluate.compute_perplexity(
                samples=samples,
                perplexity_batch_size=cfg.eval.perplexity_batch_size,
            )
            dist.all_reduce(perplexity, dist.ReduceOp.AVG)

            entropy = evaluate.compute_entropy(samples=samples)
            dist.all_reduce(entropy, dist.ReduceOp.AVG)

            if rank == 0:
                ppl_val = perplexity.item() if torch.is_tensor(perplexity) else perplexity
                ent_val = entropy.item() if torch.is_tensor(entropy) else entropy
                
                print(f"Perplexity: {ppl_val:.2f}, Entropy: {ent_val:.2f}")

                # [추가] Perplexity 결과 파일 저장
                save_path = os.path.join(work_dir, "eval_results.json")
                metrics = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "metric_type": "generation",
                    "perplexity": ppl_val,
                    "entropy": ent_val
                }
                try:
                    with open(save_path, "a") as f:
                        f.write(json.dumps(metrics) + "\n")
                    print(f"Metrics saved to {save_path}")
                except Exception as e:
                    print(f"Failed to save metrics: {e}")

        if eval_elbo:
            data_state = data._get_dataset(
                name=elbo_data,
                mode="validation",
                cache_dir=cfg.data.cache_dir,
                block_size=cfg.model.length,
                num_proc=cfg.data.num_workers,
                batch_size=batch_size,
                ngpus=world_size,
            )

            dataloader = DataLoader(
                data_state.dataset,
                batch_size=batch_size,
                sampler=data_state.sampler,
                num_workers=cfg.data.num_workers,
                pin_memory=True,
                shuffle=(data_state.sampler is None),
            )

            elbo, num_elements = evaluate.estimate_likelihood(
                model=model,
                dataloader=dataloader,
                source_distribution=source_distribution,
                n_discretization=n_discretization,
                device=device,
                batch_size=batch_size,
                path=path,
            )
            dist.barrier()

            dist.all_reduce(elbo, dist.ReduceOp.SUM)
            dist.all_reduce(num_elements, dist.ReduceOp.SUM)

            if rank == 0:
                elbo_val = torch.exp(elbo / num_elements).item()
                print(f"ELBO: {elbo_val:.2f}")

                # [추가] ELBO 결과 파일 저장
                save_path = os.path.join(work_dir, "eval_results.json")
                metrics = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "metric_type": "elbo",
                    "elbo": elbo_val,
                    "dataset": elbo_data
                }
                try:
                    with open(save_path, "a") as f:
                        f.write(json.dumps(metrics) + "\n")
                    print(f"ELBO metrics saved to {save_path}")
                except Exception as e:
                    print(f"Failed to save metrics: {e}")


def setup(rank: int, world_size: int, port: int) -> None:
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = str(port)

    torch.cuda.set_device(rank)

    timeout = datetime.timedelta(minutes=30)
    dist.init_process_group("nccl", rank=rank, world_size=world_size, timeout=timeout)


def cleanup() -> None:
    dist.destroy_process_group()


def run_mp_eval(
    rank: int,
    world_size: int,
    seed: int,
    work_dir: str,
    batch_size: int,
    sampling_steps: int,
    eval_elbo: bool,
    eval_perplexity: bool,
    elbo_data: str,
    perplexity_n_samples: int,
    port: int,
) -> None:
    try:
        setup(rank=rank, world_size=world_size, port=port)
        run_eval(
            rank=rank,
            seed=seed,
            work_dir=work_dir,
            batch_size=batch_size,
            sampling_steps=sampling_steps,
            eval_elbo=eval_elbo,
            eval_perplexity=eval_perplexity,
            elbo_data=elbo_data,
            world_size=world_size,
            perplexity_n_samples=perplexity_n_samples,
        )
    finally:
        cleanup()