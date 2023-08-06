# ProTstab2
蛋白质预测包


## 环境安装
### 模型下载
您可以通过以下两种方式下载模型:
1. https://drive.google.com/drive/folders/1OEKabeJmdGiGG1PJsPu0bgcE5_GVGXc9?usp=share_link
2. https://luke9012.lanzoub.com/b00r1vhre | password:ddpt

下载完成后，将文件夹路径传入
`p = ProTstab2(r'D:\_code\_github\ProTstab2\drop')`

### R
R语言版本需要4.1.3版本以上
同时需要安装两个包：
```
install.packages("protr")
install.packages("DT")
```
同时设置`R_HOME`到环境变量中

### Python
Python版本需要`3.6`以上


## 使用
### 如果有蛋白质序列
```python
name = "Q4JB77"
seq = "MRAAVLEEYKKPLRISEVDSPSINESSEVLLQVTATGLCHGDIHIAMGEWDSQIQVNLPIILGHEVVGRVLQSNHDKIKKNDLVLVYNAFGCKNCKYCKFKEYQFCEKVKVIGVNLNGGFAEYVKIPDGDNLVRVNTSDPIKLAPLADAGLTAYNSVKDLEENSKVLIIGTGAVALIALQLLKLKNVDVTVIGENQLKLDSAEKLGADEVISIKREEDSYLSLLPGKKFDYILDYVGSTRTLAESPWLLNKKGELRIIGEFGGVLRAEEQLLVLRGLRIRGILYGSLQDLKHILDIYLKGKIDTLTTVYKLEDINEAITDVTEGKVVGRAVIVP"
p = ProTstab2(r'D:\_code\_github\ProTstab2\drop')
r, r2 = p.predict(name, seq)
print(r, r2)
# 0.8722285 Thermophilic protein
```
### 如果没有蛋白质序列，可以使用以下方式
方式一：
```python
name = "Q4JB77"
p = ProTstab2(r'D:\_code\_github\ProTstab2\drop')
seq = p.get_seq_info(name)
r, r2 = p.predict(name, seq)
print(r, r2)
# 0.8722285 Thermophilic protein
```
方式二：
```python
name = "Q4JB77"
p = ProTstab2(r'D:\_code\_github\ProTstab2\drop')
r, r2 = p.predict(name)
print(r, r2)
# 0.8722285 Thermophilic protein
```
这里建议使用第一种方式，原因如下：
1. 由于使用爬虫的方式，所以不保证每次都能拿到数据，程序可能崩溃
2. 你可以获取到具体的蛋白质序列的值，方便后期处理

## 免责声明
本包涉及到的应用仅供学习交流使用，不得用于任何商业用途。 由此引发的任何法律纠纷与本人无关！