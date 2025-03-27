class CmlAutoCompleteTool < Formula
  include Language::Python::Virtualenv

  desc "A CLI tool that converts natural language to terminal commands using AI"
  homepage "https://github.com/yourusername/cml-auto-complete-tool"
  url "https://github.com/yourusername/cml-auto-complete-tool/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "" # You'll need to update this after creating the release

  depends_on "python@3.8"

  resource "click" do
    url "https://files.pythonhosted.org/packages/00/2e/d53fa4befbf2cfa713304affc7ca780f4b0ee0e6e01b5a8986b0c6d0f4c0/click-8.1.7.tar.gz"
    sha256 "ca9853ad459e787e2192211578cc907e7594e294c7ccc834310722b41b9ca6de"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/11/23/814edf09ec9280befbc3401a2106e3e242a3a6f2c2c0c3b4d2b9f3f4e9c/rich-13.7.0.tar.gz"
    sha256 "9be308cb1fe2f1f57d67c99ce7c245dc9d6c21166c6d993748cc66c999fff8e3"
  end

  resource "openai" do
    url "https://files.pythonhosted.org/packages/49/fe/c21d95ab120ffe4db5f850360ed997dd37bed37cd4146890488c9c594d5c/openai-1.12.0.tar.gz"
    sha256 "1d0d47965029edc6d263a206bed83a7bcdb77b0f69f69f5a1e7a685470bf27e0"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/bc/57/e84d88dfe0aec03fbcf2902cd138fbdec1cef7771297c254b4f0b0a1ee64/python-dotenv-1.0.0.tar.gz"
    sha256 "8c10be99d9b330767af9e58922b17d07893700098b8248fa09d4973c6e1726f3"
  end

  resource "prompt_toolkit" do
    url "https://files.pythonhosted.org/packages/cc/c6/25b6a3d5cd295304de1e32c9edbcf319a52e965b339629d37d42bb7126ca/prompt_toolkit-3.0.43.tar.gz"
    sha256 "9aba952f9ec1a8952f24d3d5fce1b13ff989788f7fbe2c505c50d049e894d9a"
  end

  resource "pyyaml" do
    url "https://files.pythonhosted.org/packages/cd/e5/af35f7ea75cf72f2cd079c95ee16797de7cd71f29ea7c68ae5ce7be1eda0/PyYAML-6.0.1.tar.gz"
    sha256 "bfdf460b1736c775f2ba9f6a92bca30bc2095067b8a9d77876d1fad6cc3b4a43"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/cml-auto-complete-tool", "--help"
  end
end 