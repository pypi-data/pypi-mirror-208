import os.path
import pickle
import zipfile

import numpy as np
import pandas as pd
import requests
import tensorflow as tf
from sklearn.preprocessing import RobustScaler
from tensorflow.python.keras.preprocessing import sequence

from ProTstab2.utils import Attention, get_feature_from_profeat_replace, trans, trans_6, zero_or_one


class ProTstab2:
    def __init__(self, base_model_path):
        self.base_model_path = base_model_path
        self.deep_tp_model_name = 'model_DeepTP.h5'
        self.deep_tp_model_name_zip = 'model_DeepTP.zip'
        self.features_model_name = 'selector_RFECV_205_0711_797features.pickle'
        self.features_model_name_zip = 'selector_RFECV_205_0711_797features.zip'
        self.csv_name = 'train_features.csv'
        self.csv_name_zip = 'train_features.zip'
        self.download_msg = f"""
You can download the model in either of the following two ways:
1. https://drive.google.com/drive/folders/1OEKabeJmdGiGG1PJsPu0bgcE5_GVGXc9?usp=share_link
2. https://luke9012.lanzoub.com/b00r1vhre | password:ddpt
"""
        self._check()

        # 乏了，就这么写吧，懒得改了
        self.get_model = None
        self.new_model = None
        self.test_data_x = None
        self.load_models()

    def _unzip(self, p):
        f = zipfile.ZipFile(p, 'r')  # 压缩文件位置
        for file in f.namelist():
            f.extract(file, self.base_model_path)  # 解压位置
        f.close()

    def _exists(self, p, pz):
        tmp = os.path.join(self.base_model_path, p)
        if not os.path.exists(tmp):
            tmpz = os.path.join(self.base_model_path, pz)
            if os.path.exists(tmpz):
                self._unzip(tmpz)
            else:
                raise OSError(f'{pz} file not found, please download it from {self.download_msg}')
        if not os.path.exists(tmp):
            raise OSError(f'{p} file not found, please download it from {self.download_msg}')

    def _check(self):
        assert os.path.exists(self.base_model_path), 'path does not exist'
        self._exists(self.deep_tp_model_name, self.deep_tp_model_name_zip)
        self._exists(self.features_model_name, self.features_model_name_zip)
        self._exists(self.csv_name, self.csv_name_zip)

    def load_models(self):
        with open(os.path.join(self.base_model_path, self.features_model_name), 'rb') as f:
            self.get_model = pickle.load(f)
        new_model = tf.keras.models.load_model(os.path.join(self.base_model_path, self.deep_tp_model_name),
                                               custom_objects={'Attention': Attention})
        new_model.summary()
        self.new_model = new_model

        test_data = pd.read_csv(os.path.join(self.base_model_path, self.csv_name), index_col=0)
        test_data = test_data[test_data['Sequence'].str.len() <= 1500]
        test_data_x = test_data.drop(['uniprot_id', 'Sequence', 'temp'], axis=1).select_dtypes(exclude=['object'])
        self.test_data_x = test_data_x

    def predict(self, name, seq=None):
        if seq is None:
            seq = self.get_seq_info(name)
        support = self.get_model.get_support(True)
        res = get_feature_from_profeat_replace(name, seq)
        rbs = RobustScaler()
        rbs.fit_transform(self.test_data_x)
        res_1 = rbs.transform(res)
        x_bio_data = np.array([res_1[1]])[:, support]

        test_t_x = trans(seq)
        test_t_x = [test_t_x]
        max_length = 1500
        test_t_x = sequence.pad_sequences(test_t_x, maxlen=max_length)
        x_test_t_1 = np.reshape(test_t_x, (test_t_x.shape[0], 1500, 1))
        test_t_x_6 = trans_6(seq)
        test_t_x_6 = [test_t_x_6]
        max_length = 1500
        test_t_x_6 = sequence.pad_sequences(test_t_x_6, maxlen=max_length)
        x_test1_t_6 = np.reshape(test_t_x_6, (test_t_x_6.shape[0], 1500, 1))
        result = self.new_model.predict([x_test_t_1, x_test1_t_6, x_bio_data])
        # print(result.flatten())
        result1 = list(map(zero_or_one, result))
        # print(result1)
        return result.flatten()[0], 'Thermophilic protein' if result1[0] == 1 else 'Mesophilic protein'

    @staticmethod
    def get_seq_info(pr_id):
        headers = {
            'authority': 'www.uniprot.org',
            'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh;q=0.9',
        }
        pr_id = pr_id.split("_")[0] if "_" in pr_id else pr_id
        url = "https://www.uniprot.org/uniprot/" + pr_id
        res_fasta = requests.get(url + ".fasta", headers, verify=False)
        try:
            out_simple = "".join(res_fasta.text.split("\n")[1:])
        except IndexError:
            out_simple = ""
        if '<html' in out_simple or 'http:' in out_simple:
            # out_simple = ErrorMsg("爬虫网站挂了，别试了")
            raise Exception("There are some errors with input. Please have a check.(Maybe the website is down)")
        return out_simple


if __name__ == '__main__':
    name = "Q4JB77"
    seq = "MRAAVLEEYKKPLRISEVDSPSINESSEVLLQVTATGLCHGDIHIAMGEWDSQIQVNLPIILGHEVVGRVLQSNHDKIKKNDLVLVYNAFGCKNCKYCKFKEYQFCEKVKVIGVNLNGGFAEYVKIPDGDNLVRVNTSDPIKLAPLADAGLTAYNSVKDLEENSKVLIIGTGAVALIALQLLKLKNVDVTVIGENQLKLDSAEKLGADEVISIKREEDSYLSLLPGKKFDYILDYVGSTRTLAESPWLLNKKGELRIIGEFGGVLRAEEQLLVLRGLRIRGILYGSLQDLKHILDIYLKGKIDTLTTVYKLEDINEAITDVTEGKVVGRAVIVP"
    p = ProTstab2(r'D:\_code\_github\ProTstab2\drop')
    r, r2 = p.predict(name, seq)
    print(r, r2)
