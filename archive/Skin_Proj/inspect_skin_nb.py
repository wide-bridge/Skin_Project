import json, re, pathlib
paths = [
 r'D:\PyProject\datasets\skinAI\korea_skin_data\model_and_data\docker_image\skin_dataset\data_and_model\model_train\이마주름모델.ipynb',
 r'D:\PyProject\datasets\skinAI\korea_skin_data\model_and_data\docker_image\skin_dataset\data_and_model\model_train\이마_주름_색소모델.ipynb',
 r'D:\PyProject\datasets\skinAI\korea_skin_data\model_and_data\docker_image\skin_dataset\data_and_model\model_train\모공 갯수와 주름등급 예측.ipynb',
]
pat = re.compile(r'requires_grad|freeze|unfreeze|param\\.requires_grad|EfficientNet|efficientnet|CrossEntropyLoss|WeightedRandomSampler|AdamW|Adam\\(|SGD\\(|epochs|num_epochs|learning_rate|\\blr\\s*=|scheduler|train_test_split|random_split|bbox|crop', re.I)
for p in paths:
    print('\n### FILE:', p)
    nb = json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
    for i, cell in enumerate(nb.get('cells', [])):
        if cell.get('cell_type') != 'code':
            continue
        src = ''.join(cell.get('source', []))
        if pat.search(src):
            print(f'--- CELL {i} ---')
            print(src[:4000])
            print()
