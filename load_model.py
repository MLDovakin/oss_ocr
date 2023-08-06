import os
import torch
import pandas  as pd
import yaml

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


from ocr_sub.EasyOCR.trainer.utils import AttnLabelConverter
from ocr_sub.EasyOCR.trainer.model import Model
import torch
from collections import OrderedDict
from ocr_sub.EasyOCR.trainer.dataset import AlignCollate
import torch.nn.functional as F
from ocr_sub.EasyOCR.trainer.utils import AttrDict



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
def get_config(file_path):
    with open(file_path, 'r', encoding="utf8") as stream:
        opt = yaml.safe_load(stream)
    opt = AttrDict(opt)
    if opt.lang_char == 'None':
        characters = ''
        for data in opt['select_data'].split('-'):
            csv_path = os.path.join(opt['train_data'], data, 'labels.csv')
            df = pd.read_csv(csv_path, sep='^([^,]+),', engine='python', usecols=['filename', 'words'], keep_default_na=False,dtype={'filename':str,'words':str})
            all_char = ''.join(df['words'])
            characters += ''.join(set(all_char))
        characters = sorted(set(characters))
        opt.character= ''.join(characters)
    else:
        opt.character = opt.number + opt.symbol + opt.lang_char
    os.makedirs(f'./saved_models/{opt.experiment_name}', exist_ok=True)
    return opt

def load_model(saved_model,opt):
   if opt.rgb:
       opt.input_channel=3

   converter=AttnLabelConverter(opt.character)
   num_class=len(converter.character)
   model=Model(opt).to(device)
   #print('model input parameters', opt.imgH, opt.imgW, opt.num_fiducial, opt.input_channel, opt.output_channel,
          #opt.hidden_size, opt.num_class, opt.batch_max_length, opt.Transformation, opt.FeatureExtraction,
          #opt.SequenceModeling, opt.Prediction)
              # input_channel=opt.input_channel,
              # output_channel=opt.output_channel,
              # hidden_size=opt.hidden_size,
              # num_class=num_class).to(device)
   #print(opt.saved_model)
   another_dict=OrderedDict()
   original_dict=torch.load(saved_model,map_location=device)
   for k,v in original_dict.items():
     another_dict[k.replace('module.','')]=v
   model.load_state_dict(another_dict)
   return model
def inference(model,image,opt):
  converter=AttnLabelConverter(opt.character)
  align_collate=AlignCollate(imgH=opt.imgH,
                             imgW=opt.imgW,
                             keep_ratio_with_pad=opt.PAD,
                             contrast_adjust=opt.contrast_adjust)#,
                             #apply_aug=False)
  model.eval()
  with torch.no_grad():
    image_tensors,_=align_collate([(image,None)])
    batch_size=image_tensors.size(0)
    image=image_tensors.to(device)
    length_for_pred=torch.IntTensor([opt.batch_max_length]*batch_size).to(device)
    text_for_pred=torch.LongTensor(batch_size,opt.batch_max_length+1).fill_(0).to(device)


    if 'CTC' in opt.Prediction:
      preds=model(image,text_for_pred)
      preds_size=torch.IntTensor([preds.size(1)]*batch_size)
      _,preds_index=preds.max(2)
      preds_str=converter.decode(preds_index,preds_size)
    else:
      preds=model(image,text_for_pred,is_train=False)
      _,preds_index=preds.max(2)
      preds_str=converter.decode(preds_index,length_for_pred)
    preds_prob=F.softmax(preds,dim=2)
    preds_max_prob,_=preds_prob.max(dim=2)
    prediction=None
    for pred,pred_max_prob in zip(preds_str,preds_max_prob):
      if 'Attn' in opt.Prediction:
        pred_EOS=pred.find('[s]')
        pred=pred[:pred_EOS]
        pred_max_prob=pred_max_prob[:pred_EOS]
        confidence_score=pred_max_prob.cumprod(dim=0)[-1]
        prediction=pred
        break

    return prediction
