#%%
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.fft as fft
class ResidualBlock1D(nn.Module):

    def __init__(self, planes, downsample=True):
        super(ResidualBlock1D, self).__init__()
        self.c1 = nn.Conv1d(planes,   planes,   kernel_size=1, stride=1, bias=False)
        self.b1 = nn.BatchNorm1d(planes)
        self.c2 = nn.Conv1d(planes,   planes, kernel_size=11, stride=1,
                     padding=5, bias=False)
        self.b2 = nn.BatchNorm1d(planes)
        self.c3 = nn.Conv1d(planes, planes, kernel_size=1, stride=1, bias=False)
        self.b3 = nn.BatchNorm1d(planes)
        self.downsample = nn.Sequential(
            nn.Conv1d(planes,   planes,   kernel_size=1, stride=1, bias=False),
            nn.BatchNorm1d(planes),
        )
        self.relu  = nn.ReLU(inplace=True)

    def forward(self, x):
        identity = x

        out = self.c1(x)
        out = self.b1(out)
        out = self.relu(out)

        out = self.c2(out)
        out = self.b2(out)
        out = self.relu(out)

        out = self.c3(out)
        out = self.b3(out)

        if self.downsample:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        return out


class signal_classfiy(nn.Module):
    def __init__(self):
        super(signal_classfiy,self).__init__()
        temp = 600
        self.rnn = nn.LSTM(
            input_size=50000,
            hidden_size=temp,
            num_layers=2,
            batch_first=True
        )
        self.out = nn.Sequential(
            nn.Linear(temp, 256),
            nn.ReLU(),
            nn.Linear(256, 2),
            nn.Softmax()
        )
    def forward(self,x):
        r_out,(_,_)= self.rnn(x, None)  # None表示零初始隐藏状态
        # choose r_out at the last time step
        out = self.out(r_out[:, -1, :])
        return out
# 定义residual
class RB(nn.Module):
    def __init__(self, nin, nout, ksize=3, stride=1, pad=1):
        super(RB, self).__init__()
        self.rb = nn.Sequential(nn.Conv1d(nin, nout, ksize, stride, pad),
                                nn.BatchNorm1d(nout),
                                nn.ReLU(inplace=True),
                                nn.Conv1d(nin, nout, ksize, stride, pad),
                                nn.BatchNorm1d(nout))
    def forward(self, input):
        x = input
        x = self.rb(x)
        x = F.relu(input + x)
        return x


# 定义SE模块
class SE(nn.Module):
    def __init__(self, nin, nout, reduce=16):
        super(SE, self).__init__()
        self.gp = nn.AdaptiveAvgPool1d(1)
        self.rb1 = RB(nin, nout)
        self.se = nn.Sequential(nn.Linear(nout, nout // reduce),
                                nn.ReLU(inplace=True),
                                nn.Linear(nout // reduce, nout),
                                nn.Sigmoid())
    def forward(self, input):
        x = input
        x = self.rb1(x)

        b, c, _ = x.size()
        y = self.gp(x).view(b, c)
        y = self.se(y).view(b, c, 1)
        y = x * y.expand_as(x)
        out = y + input
        return out



class model(nn.Module):
    def __init__(self,**kwargs):
        super(model, self).__init__()
        kernel_length = kwargs['kernel_length']
        class_num = kwargs['class_num']
        self.kernal_num = 256
        self.conv1d = nn.Conv1d(in_channels=1,out_channels=self.kernal_num,kernel_size=kernel_length,stride=1,padding=2)
        self.se = SE(256,256)
        self.conv1d2 = nn.Conv1d(in_channels=self.kernal_num, out_channels=self.kernal_num, kernel_size=kernel_length, stride=1,
                                padding=2)
        self.res1d1 = ResidualBlock1D(self.kernal_num)
        self.pool1  = nn.AvgPool1d(kernel_size=kernel_length,stride=1)
        self.res1d2 = ResidualBlock1D(self.kernal_num)
        self.pool2 = nn.AvgPool1d(kernel_size=kernel_length, stride=1)
        self.res1d3 = ResidualBlock1D(self.kernal_num)
        self.avgpool = nn.AdaptiveAvgPool1d(1)
        self.bn1 = nn.BatchNorm1d(1)
        self.avgpool1 = nn.AvgPool1d(kernel_size=2,stride=2)
        self.liner = nn.Sequential(
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(in_features=self.kernal_num,out_features=class_num),
        )
    def forward(self,x:torch.tensor,**kwargs):
        x = self.bn1(x)
        x = self.avgpool1(x)
        x = self.conv1d(x)
        x = self.se(x)
        x = self.conv1d2(x)
        x = self.res1d1(x)
        x = self.pool1(x)
        x = self.res1d2(x)
        x = F.dropout(input=x, p=0.2, training=True)
        x = self.pool2(x)
        x = self.res1d3(x)
        x = F.dropout(input=x, p=0.2, training=True)
        x = self.avgpool(x)
        x = self.liner(x)
        return x
