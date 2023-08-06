import torch
from sklearn import metrics
from torch.optim import Optimizer

class Model(torch.nn.Module):
    """Wrap your model with this class and train your model easly
    
    """
    
    available_metrics = {
        'accuracy': metrics.accuracy_score,
        'f1_score': metrics.f1_score,
        'precision': metrics.precision_score,
        'recall': metrics.recall_score,
        'mse': metrics.mean_squared_error,
        'mae': metrics.mean_absolute_error,
        # 'roc_auc': metrics.roc_auc_score,
    }
    
    optimizers = {
        'adam': torch.optim.Adam,
        'adamw': torch.optim.AdamW,
        'nadam': torch.optim.NAdam,
        'sgd': torch.optim.SGD,
    }
    
    criterions = {
        'cross_entropy': torch.nn.CrossEntropyLoss,
        'mse': torch.nn.MSELoss,
    }
    
    
    def __init__(self):
        super(Model, self).__init__()
        
        self.callbacks = []
        self.optimizer = None
        self.metrics = []
        self.device = None
        self.build_model = False
    
    def build(
            self,
            optimizer='adam',
            criterion='cross_entropy',
            metrics=['accuracy'],
            callbacks=[],
            device='cuda'
        ):
        self.optimizer = optimizer
        if optimizer in self.optimizers:
            self.optimizer = self.optimizers[optimizer](self.parameters())
        
        self.criterion = criterion
        if criterion in self.criterions:
            self.criterion = self.criterions[criterion]()
        
        # let's check criterion and optimizer
        self._check_optimizer(self.optimizer)
        self._check_criterion(self.criterion)
        
        for metric in metrics:
            self.add_metric(metric)
        
        self.callbacks.extend(callbacks)    
        
        if device == 'cpu':
            self.device = device
        else:
            if not torch.cuda.is_available():
                print('W: cuda is not available, using cpu!')
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.build_model = True

    def _train_epoch(self, dataloader):
        self.train()

        cur_loss = 0
        total_data = 0
        
        y_actual = []
        y_preds = []
        for x_batch, y_batch in dataloader:
            x_batch, y_batch = x_batch.to(self.device), y_batch.to(self.device)
            self.optimizer.zero_grad()
            
            output = self(x_batch)
            loss = self.criterion(output, y_batch)
            loss.backward()
            self.optimizer.step()
            
            preds = output.argmax(-1)

            cur_loss += loss.item() * x_batch.size(0)
            total_data += x_batch.size(0)
            
            y_actual.extend(y_batch.cpu().numpy())
            y_preds.extend(preds.cpu().numpy())

        epoch_loss = cur_loss / total_data
        
        return epoch_loss, self._get_metrics(y_actual, y_preds)

    def _eval_epoch(self, dataloader):
        self.eval()

        cur_loss = 0
        total_data = 0
        y_actual = []
        y_preds = []
        for x_batch, y_batch in dataloader:
            x_batch, y_batch = x_batch.to(self.device), y_batch.to(self.device)

            with torch.no_grad():
                output = self(x_batch)
                loss = self.criterion(output, y_batch)
                preds = output.argmax(-1)

            cur_loss += loss.item() * x_batch.size(0)
            total_data += x_batch.size(0)
            
            y_actual.extend(y_batch.cpu().numpy())
            y_preds.extend(preds.cpu().numpy())

        loss = cur_loss / total_data

        return loss, self._get_metrics(y_actual, y_preds)


    def _get_metrics(self, y_true, y_pred):
        metrics = {}
        for metric in self.metrics:
            if metric == 'accuracy':
                metrics[metric] = self.available_metrics[metric](y_true, y_pred)
            elif metric == 'mse' or metric == 'mae':
                metrics[metric] = self.available_metrics[metric](y_true, y_pred)
            else:
                metrics[metric] = self.available_metrics[metric](y_true, y_pred, average='micro')
        return metrics

    def fit(
            self,
            train_data,
            validation_data=None,
            epochs=5,
            verbose=True
        ):
        if self.build_model is False:
            self.build() # build model with default parameters
        
        self.to(self.device)
        
        history = {}
        n_bits = len(str(epochs))
        for epoch in range(epochs):
            epoch_statistics = {}
            train_loss, train_metrics = self._train_epoch(train_data)
            epoch_statistics['train_loss'] = train_loss
            if validation_data is not None:
                val_loss, val_metrics = self._eval_epoch(validation_data)
                epoch_statistics['val_loss'] = val_loss
            
            for metric in self.metrics:
                epoch_statistics[f'train_{metric}'] = train_metrics[metric]
                if validation_data is not None: 
                    epoch_statistics[f'val_{metric}'] = val_metrics[metric]


            # fill logs for output, if verbose is True
            logs = []
            logs.append(f'epoch {(epoch+1):0{n_bits}d}/{epochs:0{n_bits}d}')
            for stat in epoch_statistics:
                val = epoch_statistics[stat]
                logs.append(f'{stat}: {val:0.4f}')
                
                if stat not in history:
                    history[stat] = []
                    
                history[stat].append(val)
            
            # call all callbacks here, add them in log if needed
            for callback in self.callbacks:
                try:
                    callback.step()
                except Exception as _:
                    print(f'Callback {callback} should have step() method, which is called after each epoch!')

            if verbose is True:
                print(' | '.join(logs))

        return history
    
    
    def add_callback(self, callbacks):
        self.callbacks.extend(callbacks)
    
    
    def add_metric(self, metric):
        if metric not in self.available_metrics:
            raise TypeError(f"Metric '{metric}' not supported, available metrics are: {self.available_metrics.keys()}")
        self.metrics.append(metric)
    
    
    def _check_optimizer(self, optimizer):
        if not isinstance(optimizer, Optimizer):
            raise TypeError(f"Optimizer {type(optimizer).__name__} is not an optimizer")
    
     
    def _check_criterion(self, criterion):
        # TODO: this is bad way of checking criterion fix it
        type_ = str(type(criterion)).split("'")[1]
        parent = type_.rsplit(".", 1)[0]
        if parent != "torch.nn.modules.loss":
            raise TypeError(f"Criterion {type(criterion).__name__} is not an loss function")
