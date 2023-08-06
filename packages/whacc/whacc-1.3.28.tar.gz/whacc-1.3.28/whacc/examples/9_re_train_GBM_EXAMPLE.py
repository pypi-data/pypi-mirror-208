
from whacc import utils
import numpy as np
from whacc.retrain_LGBM import retrain_LGBM

bd = '/Users/phil/Desktop/untitled folder/'
labels_key = 'labels'
h5_list = utils.get_files(bd, '*.h5')
tvt_x, tvt_y, tvt_fn, tvt_w = utils.load_training_and_curated_data(h5_list, labels_key)


model_base_dir = '/Users/phil/Desktop/tmp_mod_test/'
study_name = 'my_custom_optuna_models_test_V2'

#VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
load_optuna_if_exists = False # change to true if continuing training<<<<<<<<<<<<<<<<
#AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

rm = retrain_LGBM(model_base_dir, study_name, tvt_x, tvt_y, tvt_fn, tvt_w, load_optuna_if_exists=load_optuna_if_exists)

rm.GLOBALS['num_optuna_trials'] = 20  ########  20  3
rm.GLOBALS['early_stopping_rounds'] = 100  ########  100 10
rm.GLOBALS['num_iterations'] = 1000 ########  10000 5




rm.train_model()


# after doubling
tot = 526222+147854+70924
526222/tot, 147854/tot, 70924/tot
#percent each of total
(0.7063382550335571, 0.19846174496644295, 0.0952)
# percent touch
0.43341783505820736
0.4155315378684378
0.3958039591675596



tmp1 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/models/all_pred_dict.pkl'
tmp1 = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/models/all_pred_dict3.pkl'
tmp1 = utils.load_obj(tmp1)

utils.info(tmp1)

all_sizes = []
for k in tmp1:
    all_sizes.append(len(tmp1[k]))

# all validation set sizes for 10 models.... ([212740, 212746, 212754, 212764, 212765, 212821, 212823, 212859, 212866, 212867])
#  toal of 2,128,005
keys = list(tmp1.keys())
tmp2 = tmp1[keys[-1]]

import matplotlib.pyplot as plt
plt.plot(tmp2[-4000:])
# import matplotlib.pyplot as plt
# for k in tvt_y:
#     print(np.mean(k))
# plt.ylim(0, 1)



