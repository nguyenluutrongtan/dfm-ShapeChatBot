from setuptools import setup, find_packages

setup(
    name="dfm-shape-chatbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "python-dotenv",
        "openai",
    ],
    author="Nguyễn Lưu Trọng Tấn",
    author_email="nguyenluutrongtantan@gmail.com",
    description="A chatbot for drawing geometric shapes",
    long_description=open("docs/README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/nguyenluutrongtan/dfm-ShapeChatBot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 