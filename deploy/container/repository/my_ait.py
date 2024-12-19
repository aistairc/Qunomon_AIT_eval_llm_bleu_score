#!/usr/bin/env python
# coding: utf-8

# # AIT Development notebook

# ## notebook of structure

# | #  | Name                                               | cells | for_dev | edit               | description                                                                |
# |----|----------------------------------------------------|-------|---------|--------------------|----------------------------------------------------------------------------|
# | 1  | [Environment detection](##1-Environment-detection) | 1     | No      | uneditable         | detect whether the notebook are invoked for packaging or in production     |
# | 2  | [Preparing AIT SDK](##2-Preparing-AIT-SDK)         | 1     | Yes     | uneditable         | download and install AIT SDK                                               |
# | 3  | [Dependency Management](##3-Dependency-Management) | 3     | Yes     | required(cell #2)  | generate requirements.txt for Docker container                             |
# | 4  | [Importing Libraries](##4-Importing-Libraries)     | 2     | Yes     | required(cell #1)  | import required libraries                                                  |
# | 5  | [Manifest Generation](##5-Manifest-Generation)     | 1     | Yes     | required           | generate AIT Manifest                                                      |
# | 6  | [Prepare for the Input](##6-Prepare-for-the-Input) | 1     | Yes     | required           | generate AIT Input JSON (inventory mapper)                                 |
# | 7  | [Initialization](##7-Initialization)               | 1     | No      | uneditable         | initialization for AIT execution                                           |
# | 8  | [Function definitions](##8-Function-definitions)   | N     | No      | required           | define functions invoked from Main area.<br> also define output functions. |
# | 9  | [Main Algorithms](##9-Main-Algorithms)             | 1     | No      | required           | area for main algorithms of an AIT                                         |
# | 10 | [Entry point](##10-Entry-point)                    | 1     | No      | uneditable         | an entry point where Qunomon invoke this AIT from here                     |
# | 11 | [License](##11-License)                            | 1     | Yes     | required           | generate license information                                               |
# | 12 | [Deployment](##12-Deployment)                      | 1     | Yes     | uneditable         | convert this notebook to the python file for packaging purpose             |

# ## notebook template revision history

# 1.0.1 2020/10/21
# 
# * add revision history
# * separate `create requirements and pip install` editable and noeditable
# * separate `import` editable and noeditable
# 
# 1.0.0 2020/10/12
# 
# * new cerarion

# ## body

# ### #1 Environment detection

# [uneditable]

# In[1]:


# Determine whether to start AIT or jupyter by startup argument
import sys
is_ait_launch = (len(sys.argv) == 2)


# ### #2 Preparing AIT SDK

# [uneditable]

# In[2]:


if not is_ait_launch:
    # get ait-sdk file name
    from pathlib import Path
    from glob import glob
    import re
    import os

    current_dir = get_ipython().run_line_magic('pwd', '')

    ait_sdk_path = "./ait_sdk-*-py3-none-any.whl"
    ait_sdk_list = glob(ait_sdk_path)
    ait_sdk_name = os.path.basename(ait_sdk_list[-1])

    # install ait-sdk
    get_ipython().system('pip install -q --upgrade pip')
    get_ipython().system('pip install -q --no-deps --force-reinstall ./$ait_sdk_name')


# ### #3 Dependency Management

# #### #3-1 [uneditable]

# In[3]:


if not is_ait_launch:
    from ait_sdk.common.files.ait_requirements_generator import AITRequirementsGenerator
    requirements_generator = AITRequirementsGenerator()


# #### #3-2 [required]

# In[4]:


if not is_ait_launch:
    requirements_generator.add_package('mlflow','2.18.0')
    requirements_generator.add_package('pandas', '2.2.3')
    requirements_generator.add_package('evaluate', '0.4.3')
    requirements_generator.add_package('transformers', '4.46.3')
    requirements_generator.add_package('torch', '2.5.1')
    requirements_generator.add_package('torchvision', '0.20.1')
    requirements_generator.add_package('torchaudio', '2.5.1')


# #### #3-3 [uneditable]

# In[5]:


if not is_ait_launch:
    requirements_generator.add_package(f'./{ait_sdk_name}')
    requirements_path = requirements_generator.create_requirements(current_dir)

    get_ipython().system('pip install -q -r $requirements_path ')


# ### #4 Importing Libraries

# #### #4-1 [required]

# In[6]:


# import if you need modules cell

import mlflow
import os
import pandas as pd
import json
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
import torch


# #### #4-2 [uneditable]

# In[7]:


# must use modules
from os import path
import shutil  # do not remove
from ait_sdk.common.files.ait_input import AITInput  # do not remove
from ait_sdk.common.files.ait_output import AITOutput  # do not remove
from ait_sdk.common.files.ait_manifest import AITManifest  # do not remove
from ait_sdk.develop.ait_path_helper import AITPathHelper  # do not remove
from ait_sdk.utils.logging import get_logger, log, get_log_path  # do not remove
from ait_sdk.develop.annotation import measures, resources, downloads, ait_main  # do not remove
# must use modules


# ### #5 Manifest Generation

# [required]

# In[8]:


if not is_ait_launch:
    from ait_sdk.common.files.ait_manifest_generator import AITManifestGenerator
    manifest_genenerator = AITManifestGenerator(current_dir)
    manifest_genenerator.set_ait_name('eval_llm_bleu_score')
    manifest_genenerator.set_ait_description('MLFlowを使用して、LLMモデルで問題領域の質問に対して回答し、その生成されたテキストの品質を評価します。LLM評価基準を用いて、回答テキストのBLEUスコアを計算し、テキストの質を数値化します。')
    manifest_genenerator.set_ait_source_repository('https://github.com/aistairc/Qunomon_AIT_eval_llm_bleu_score')
    manifest_genenerator.set_ait_version('1.0')
    manifest_genenerator.add_ait_licenses('Apache License Version 2.0')
    manifest_genenerator.add_ait_keywords('LLM')
    manifest_genenerator.add_ait_keywords('MLFlow')
    manifest_genenerator.add_ait_keywords('BLEU')
    manifest_genenerator.set_ait_quality('https://ait-hub.pj.aist.go.jp/ait-hub/api/0.0.1/qualityDimensions/機械学習品質マネジメントガイドライン第三版/C-1機械学習モデルの正確性')
    inventory_requirement_data = manifest_genenerator.format_ait_inventory_requirement(format_=['json'])
    manifest_genenerator.add_ait_inventories(name='question_data', 
                                              type_='dataset', 
                                              description='質問と回答のペアを含むデータセット \nJSON形式{inputs:array, ground_truth:array}\n例：{inputs: [MLflowとは？], ground_truth: [MLflowは、機械学習ライフサイクルを管理するオープンプラットフォーム]}', 
                                              requirement=inventory_requirement_data)
    inventory_requirement_model = manifest_genenerator.format_ait_inventory_requirement(format_=['ALL'])
    manifest_genenerator.add_ait_inventories(name='llm_model_dir', 
                                              type_='model', 
                                              description='事前にトレーニング済みの大規模言語モデルと、そのモデルの設定ファイルを保存したディレクトリ\n 例:T5, GPT-3\n モデルファイルは、config.json, model.safetensors, generation_config.json, special_tokens_map.json, tokenizer_config.json, tokenizer.jsonを含む', 
                                              requirement=inventory_requirement_model)
    manifest_genenerator.add_ait_measures(name='BLEU_Score', 
                                           type_='float', 
                                           description='計算されたBLEUスコア', 
                                           structure='single',
                                           min='0')
    manifest_genenerator.add_ait_resources(name='sample_data_csv',  
                                           type_='table', 
                                           description='BLEUスコアが最も低い10セットのデータサンプル')
    manifest_genenerator.add_ait_downloads(name='Log', 
                                           description='AIT実行ログ')
    manifest_genenerator.add_ait_downloads(name='MLFow_eval_result', 
                                           description='MLFlow実行結果を示すCSVファイル。以下の項目を含む\n inputs:モデルに入力されたデータ\n predictions:モデルが生成した予測結果\n ground_truth:期待される正解データ\n bleu/v1/score:BLEUスコア')
    manifest_path = manifest_genenerator.write()


# ### #6 Prepare for the Input

# [required]

# In[9]:


if not is_ait_launch:
    from ait_sdk.common.files.ait_input_generator import AITInputGenerator
    input_generator = AITInputGenerator(manifest_path)
    input_generator.add_ait_inventories(name='question_data',
                                     value='question_data.json')
    input_generator.add_ait_inventories(name='llm_model_dir',
                                     value='model')
    input_generator.write()


# ### #7 Initialization

# [uneditable]

# In[10]:


logger = get_logger()

ait_manifest = AITManifest()
ait_input = AITInput(ait_manifest)
ait_output = AITOutput(ait_manifest)

if is_ait_launch:
    # launch from AIT
    current_dir = path.dirname(path.abspath(__file__))
    path_helper = AITPathHelper(argv=sys.argv, ait_input=ait_input, ait_manifest=ait_manifest, entry_point_dir=current_dir)
else:
    # launch from jupyter notebook
    # ait.input.json make in input_dir
    input_dir = '/usr/local/qai/mnt/ip/job_args/1/1'
    current_dir = get_ipython().run_line_magic('pwd', '')
    path_helper = AITPathHelper(argv=['', input_dir], ait_input=ait_input, ait_manifest=ait_manifest, entry_point_dir=current_dir)

ait_input.read_json(path_helper.get_input_file_path())
ait_manifest.read_json(path_helper.get_manifest_file_path())

### do not edit cell


# ### #8 Function definitions

# [required]

# In[11]:


@log(logger)
@measures(ait_output, 'BLEU_Score')
def mean_bleu(mean_bleu):
    return mean_bleu


# In[12]:


@log(logger)
@resources(ait_output, path_helper, 'sample_data_csv', 'sample_data_csv.csv')
def save_sample_data_csv(df, file_path: str=None) -> None:
    df.to_csv(file_path)


# In[13]:


@log(logger)
@downloads(ait_output, path_helper, 'MLFow_eval_result', 'MLFow_eval_result.csv')
def eval_result(eval_table, file_path: str=None) -> str:    
    eval_table.to_csv(file_path, index=False)


# In[14]:


@log(logger)
@downloads(ait_output, path_helper, 'Log', 'ait.log')
def move_log(file_path: str=None) -> str:
    shutil.move(get_log_path(), file_path)


# ### #9 Main Algorithms

# [required]

# In[15]:


@log(logger)
@ait_main(ait_output, path_helper, is_ait_launch)
def main() -> None:
    # 並列処理の警告を抑制
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    with open(ait_input.get_inventory_path('question_data'), "r") as file:
        json_data = json.load(file)

    eval_data = pd.DataFrame(json_data)
    
    # ローカルに保存されたLLMモデルを読み込む
    tokenizer_path = ait_input.get_inventory_path('llm_model_dir')
    model_path = ait_input.get_inventory_path('llm_model_dir')
    
    # Transformers を使用してモデルとトークナイザをロード
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

    # パイプラインの作成
    device = 0 if torch.cuda.is_available() else -1  # GPUが利用可能なら0、そうでなければ-1（CPU）
    text2text_pipeline = pipeline("text2text-generation", model=model, tokenizer=tokenizer, device=device)

    # モデルの予測関数
    def predict(inputs):
        # 入力データの正規化
        inputs = inputs.strip()

        # 複数候補を生成し、最適な結果を選択
        outputs = text2text_pipeline(
            inputs,
            max_new_tokens=50,
            num_return_sequences=3,  # 複数候補を生成
            num_beams=3  # ビームサーチを有効に
        )

        # 候補から最適なものを選択
        candidates = [output["generated_text"] for output in outputs]
        best_candidate = min(candidates, key=len)  # 最短の候補を選択（タスクに応じて変更可能）

        return best_candidate


    # 予測値を計算してデータに追加
    eval_data["predictions"] = eval_data["inputs"].apply(predict)
        
    with mlflow.start_run() as run:
        mlflow.transformers.log_model(
            transformers_model=text2text_pipeline,  # パイプラインを渡す
            artifact_path="model",
        )
        # ログされたモデルの URI を取得
        logged_model_uri = f"runs:/{run.info.run_id}/model"

        # MLflow の評価関数を使用して BLEU スコアを計算
        results = mlflow.evaluate(
            model=logged_model_uri,
            data=eval_data,
            targets="ground_truth",
            predictions="predictions",
            model_type=None,
            extra_metrics=[mlflow.metrics.bleu()] # 追加メトリクス
        )

        # 評価結果を表示
        print(f"See aggregated evaluation results below: \n{results.metrics}")

        # 評価結果テーブル
        eval_table = results.tables["eval_results_table"]
        print(f"See evaluation table below: \n{eval_table}")
        eval_result(eval_table)
        
        # BLEUの平均スコアを取得
        mean_bleu(results.metrics.get("bleu/v1/mean", 0))
        
        # BLEUスコアで昇順にソートし、上位10行を取得
        sorted_df = eval_table.sort_values(by="bleu/v1/score", ascending=True).head(10)
        save_sample_data_csv(sorted_df)
            
    # AIT実行ログ出力
    move_log()


# ### #10 Entry point

# [uneditable]

# In[16]:


if __name__ == '__main__':
    main()


# ### #11 License

# [required]

# In[17]:


ait_owner='AIST'
ait_creation_year='2024'


# ### #12 Deployment

# [uneditable] 

# In[18]:


if not is_ait_launch:
    from ait_sdk.deploy import prepare_deploy
    from ait_sdk.license.license_generator import LicenseGenerator
    
    current_dir = get_ipython().run_line_magic('pwd', '')
    prepare_deploy(ait_sdk_name, current_dir, requirements_path)
    
    # output License.txt
    license_generator = LicenseGenerator()
    license_generator.write('../top_dir/LICENSE.txt', ait_creation_year, ait_owner)
