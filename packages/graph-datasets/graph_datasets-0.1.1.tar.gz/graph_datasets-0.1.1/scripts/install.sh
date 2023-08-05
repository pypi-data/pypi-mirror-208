# # install python 3.7.16 use pyenv
# pyenv install 3.7.16
# pyenv local 3.7.16

# create and activate virtual environment
if [ ! -d '.venv' ]; then
    python3 -m venv .venv && echo create venv
else
    echo venv exists
fi

source .venv/bin/activate

# # update pip
# python -m pip install -U pip

# # torch cuda 11.3
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu113

# # dgl cuda 11.3
python -m pip install dgl -f https://data.dgl.ai/wheels/cu113/repo.html -i https://pypi.tuna.tsinghua.edu.cn/simple/
python -m pip install dglgo -f https://data.dgl.ai/wheels-test/repo.html -i https://pypi.tuna.tsinghua.edu.cn/simple/

# # install requirements
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

echo install requirements successfully!
