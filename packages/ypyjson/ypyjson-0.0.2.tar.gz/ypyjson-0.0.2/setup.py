from setuptools import setup, Extension, find_packages
import pathlib

VERSION = "0.0.2"

HERE = pathlib.Path("ypyjson")
long_description = open('README.md').read()

# with open("readme.md","r",encoding="utf-8") as r:
#     LONG_DESC = r.read()

# Name change from yapy to ypy due to contorvoursy over a guy who made a yap flag , 
# hung it up over neighbor's houses and later swats them 

def main():
    yyjson =  HERE / "yyjson"
    
    extensions = [
        Extension("ypyjson.reader", [
                str(HERE /"reader.c"), 
                str(yyjson / "yyjson.c")
            ]
        )
    ]
    
    setup(
        name="ypyjson", 
        version=VERSION,
        author="Vizonex", 
        description="""yet another python json library using yyjson""",
        long_description_content_type='text/markdown',
        long_description=long_description,
        ext_modules = extensions,
        license="Unlicense",
        packages=find_packages(
            include=['ypyjson',"ypyjson/yyjson/yyjson.c","ypyjson/yyjson/yyjson.h"],
            exclude=['ypyjson/reader.cp39-win_amd64.pyd']
            ),
        # Include cython packages , stub files and yyjson's header file
        package_data = {".": ["*.pyi","*.pxi","*.pxd","*.pyx","*.c","*.h"]},
        keywords=["yyjson", "ypyjson", "json", "cython"],
        classifiers=[
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11'
        ],
        include_package_data=True
    )

if __name__ == "__main__":
    main()
