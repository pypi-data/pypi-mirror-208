

<h1 align="center" style="text-align:center;">
  <img src="./static/logo.png" width = "270" height = "90" alt="westat logo" align=center />
</h1>

<p align="center"> 信用评分卡模型开发工具  <br />WOE和IV值计算、KS和AUC计算</p>

<p align="center" >
<a href="http://www.pyminer.com" ><img src="./static/pyminer.png" width = "25" height = "25"></a>
<a href="https://gitee.com/westat/westat"><img  src="./static/gitee.png" width = "25" height = "25"></a>
<a href="https://github.com/stat-fit/westat"><img  src="./static/github.png" width = "25" height = "25"></a>
<a href="https://pypi.org/project/westat/" ><img src="./static/pypi.png" width = "25" height = "25"></a>
<br>
<a ><img src="https://img.shields.io/static/v1?label=QQ Group&message=945391275&color=<COLOR>"></a>
<a ><img src="https://img.shields.io/static/v1?label=Mail&message=westat@foxmail.com&color=<COLOR>"></a>
</p>


<h3> 一、描述 </h3>

用于开发信用评分卡模型的python包，包含特征分箱、特征筛选、WOE和IV计算，KS值和AUC计算、模型提升度LIFT、模型稳定性 PSI 计算、决策树绘制、评分卡制作等功能

westat是开源数据分析处理项目pyminer 的一部分，但是也可以被单独使用。
westat 希望更多朋友能够参与项目，一起维护并提升！


<h3>二、交流</h3>
项目交流QQ群：945391275
<br>
可参考知乎文章，有问题请留言
<br>
<a href="https://zhuanlan.zhihu.com/p/609163039" >https://zhuanlan.zhihu.com/p/609163039 </a>


<h3> 三、安装 </h3>

```bash
pip install westat
```

<h3> 四、常见操作 </h3>
<h4>安装</h4>

```bash
import westat
westat.version
```

<h3> ks和auc计算 </h3>
<p></p>

<img src="./static/auc_ks.png"  alt="auc_ks" align=center />

<p></p>

<h3> 决策树分箱 </h3>
<p></p>
<img src="./static/tree_iv.png"  alt="tree_iv" align=center />
<img src="static/view_woe_iv.png"  alt="view_woe_iv" align=center />

<p></p>

<h3> 等频分箱 </h3>

<p></p>

<img src="./static/qcut_woe_iv.png"  alt="qcut_woe_iv" align=center />

<p></p>
<h3> 个性化分箱 </h3>

<p></p>

<img src="./static/cut_woe_iv.png"  alt="cut_woe_iv" align=center />

<p></p>
<h3> 模型提升度 Lift 计算 </h3>

<p></p>

<img src="./static/get_lift.png"  alt="get_lift" align=center />

<p></p>
<h3> 模型稳定度 PSI计算 </h3>
<p></p>

<img src="./static/get_psi.png"  alt="get_psi" align=center />

<p></p>

<h3> 评分卡制作 </h3>
<p></p>

<img src="./static/get_scorecard.png"  alt="get_scorecard" align=center />

<p></p>

<h3> 评分卡分数预测 </h3>
<p></p>

<img src="./static/predict_score.png"  alt="predict_score" align=center />

<p></p>