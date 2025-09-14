# Setup

I have created the project using the following commands:

```
conda env create -f environment.yml
conda activate wscat
uv init --name wscat --app
rm main.py
mkdir -p src/wscat/server
touch src/wscat/server/__init__.py
mv main.py src/wscat/server
```

...then added the rest. :)
