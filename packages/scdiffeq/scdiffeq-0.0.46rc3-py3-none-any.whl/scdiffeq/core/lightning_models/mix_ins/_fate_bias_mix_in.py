
import pandas as pd
import sklearn
import torch

from .. import base


class FateBiasMixIn(object):
    def __init__(self):
        super().__init__()
        
        
    def _configure_fate(
        self,
        graph,
        csv_path,
        t0_idx,
        fate_bias_multiplier = 1,
        undiff_key = "Undifferentiated",
        PCA = None,
    ):
        
        self.graph = graph
        self.fate_bias_multiplier = fate_bias_multiplier
        self.fate_df = pd.read_csv(csv_path, index_col=0)
        self.fate_df.index = t0_idx # adata.obs.loc[adata.obs['Time point']==2].index
        self._undiff_key = undiff_key

    def log_sinkhorn_divergence(self, sinkhorn_loss, t, stage, note=None):
        for i in range(len(t)):
            msg = f"sinkhorn_{t[i].item()}_{stage}"
            if note:
                msg = "_".join([note, msg])
            self.log(msg, sinkhorn_loss[i])
#             print(f"{msg} ({note}): {sinkhorn_loss[i].item()}")

        return sinkhorn_loss.sum()
    
    def fate_accuracy(self, X_hat, batch_fate_idx):

        F_true = self.fate_df.loc[batch_fate_idx]
        self.X_hat = X_hat
        F_pred = self.graph(X_hat, annot_key="Cell type annotation", query_t = -1)[0]
        F_pred.index = batch_fate_idx

        if F_pred.columns.unique().tolist() == [self._undiff_key]:
            return 0, 1

        univ_cols = [col for col in F_true.columns if col in F_pred.columns]
        F_true, F_pred = F_pred[univ_cols], F_true[univ_cols]
        acc_score = sklearn.metrics.accuracy_score(F_true.idxmax(1), F_pred.idxmax(1))
        acc_weight = 1 - acc_score
        return acc_score, acc_weight

    def step(self, batch, batch_idx=None, stage=None):
        
        
        batch = base.BatchProcessor(batch, batch_idx)
        X_hat = self.forward(Z0=batch.X0, t=batch.t)
        sinkhorn_loss = self.compute_sinkhorn_divergence(batch.X, X_hat, batch.W, batch.W_hat)
        self.log_sinkhorn_divergence(sinkhorn_loss=sinkhorn_loss, t=batch.t, stage=stage) 
        acc_score, acc_weight = self.fate_accuracy(X_hat, batch.F_idx)
        
        if not self._current_fx_name is None:
            acc_score = torch.Tensor([acc_score]).to(torch.float32)
            self.log(f"fate_acc_score_{stage}", acc_score)
            
        fate_weighted_sinkhorn_loss = sinkhorn_loss * acc_weight * self.fate_bias_multiplier
#         print("FW:", fate_weighted_sinkhorn_loss)
        self.log_sinkhorn_divergence(
            sinkhorn_loss=fate_weighted_sinkhorn_loss,
            t=batch.t,
            stage=stage,
            note="fate_weighted",
        ) 
        return sinkhorn_loss.sum() + fate_weighted_sinkhorn_loss.sum()
