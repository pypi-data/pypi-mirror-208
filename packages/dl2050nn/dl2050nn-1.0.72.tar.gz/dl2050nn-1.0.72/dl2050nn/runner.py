from pathlib import Path
import pandas as pd
import pickle
import gc
from IPython.display import display
from dl2050nn.etc import load_model, get_logprobs
from dl2050nn.results import Results_Clsf
from dl2050nn.log import key_metric

class Runner:
    def __init__(self, path, model=None, data=None, get_learner=None, nruns=10, eps=10, name='Runner', desc='', pre=None):
        self.path,self.model = path,model
        self.get_learner,self.data = get_learner,data
        self.nruns,self.eps,self.name,self.desc,self.pre = nruns,eps,name,desc,pre
        if not Path(f'{path}/runners').exists(): Path(f'{path}/runners').mkdir()
        self.fname = f'{path}/runners/{name}'
        self.learner,self.df,self.best = None,None,0.
            
    def __call__(self, show=False):
        self.model = self.model.cuda()
        self.best, self.best_file = 0., None
        for i in range(self.nruns):
            if show: print(f'\rRun {i}')
            learner = self.get_learner(model_name= f'{self.name}_{i}', pre=self.pre)
            self.learner = learner
            learner.fit(self.eps)
            learner.load(show=show)
            df1 = learner.logger.df_best
            df1['Best'] = '*' if learner.logger.best > self.best else ''
            self.df = df1.copy() if self.df is None else pd.concat((self.df,df1),ignore_index=True)
            if learner.logger.best > self.best:
                self.best,self.best_file = learner.logger.best,f'{self.name}_{i}'
                display(self.df.iloc[[-1]])
            self.save()
            learner.close()
            del learner
            gc.collect()
        self.save()
        print(f'\nBest file: {self.best_file}')
        if show: display(self.df)

    def save(self):
        meta = {'desc': self.desc, 'best': self.best, 'best_file': self.best_file}
        pickle.dump(meta, open(self.fname+'.pickle', 'wb'))
        self.df.to_csv(self.fname+'.csv', index=False)

    def load(self, show=False):
        p_pickle,p_csv = Path(f'{self.fname}.pickle'),Path(f'{self.fname}.csv')
        if not p_pickle.exists() or not p_csv.exists(): return
        meta = pickle.load(open(self.fname+'.pickle', 'rb'))
        if show: print('cols' in meta, 'best' in meta,  'best_file' in meta)
        if not 'best' in meta or not 'best_file' in meta: return
        if show: print(f'Loaded from file {self.fname}: {meta}')
        self.desc, self.best, self.best_file = meta['desc'], meta['best'], meta['best_file']
        self.df = pd.read_csv(self.fname+'.csv')
        if show: display(self.df)
        self.df['Best'] = self.df['Best'].fillna('')
        load_model(self.model, f'{self.path}/models/{self.best_file}.pth.tar', show=show, cuda=True, inference=True)

    def df_best(self):
        if self.learner is None: return None
        return self.df[self.df.iloc[:,key_metric(self.learner)]==self.best].iloc[[0]]
    
    def stats(self):
        return dict(self.df[self.df['accuracy_2']==self.df['accuracy_2'].max()].iloc[0])
    
    def show_results(self):
        self.load()
        y2,y = get_logprobs(self.model, self.data.ds2.x),self.data.ds2.y
        r = Results_Clsf(y2=y2, y=y)
        r.confusion()
        r.roc()
        r.stats()
        return r
