#python ./evaluation/eval_tum.py --cfg=cfgs/tum.yaml  --dataset_dir=data/tum --model=checkpoints/tum/tmu_model/_stage_2.ckpt  --n_iters=1
python ./evaluation/eval_tum.py --cfg=cfgs/tum_2_2_fast_shufflev2.yaml  --dataset_dir=data/tum --model=checkpoints/tum/tmu_model/_stage_2.ckpt  --n_iters=1
#python ./evaluation/eval_tum.py --cfg=cfgs/tum.yaml  --dataset_dir=data/tum --model=checkpoints/tum/tmu_model_fast_resnet/_stage_2.ckpt  --n_iters=1


