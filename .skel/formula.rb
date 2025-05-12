class Dmlpdfdateextract < Formula
  PYTHON_VERSION = "3.12"
  desc "Extracts all dates from pdf or the Nth"
  homepage "https://github.com/dmlane/pdfdateextract"
  url "https://github.com/dmlane/pdfclassify/releases/download/v1.0.28/pdfclassify-1.0.28.pyz"
  sha256 "0cc0daf087539cf49c3f32763f4357d338c4744056a651bc839e31a98f918530"
  license "MIT"

  depends_on "python@#{PYTHON_VERSION}"

  def install
    pyz = Dir["*.pyz"].first
    libexec.install pyz
	(bin/"pdfdateextract").write <<~EOS
        #!/bin/bash
        exec #{Formula["python@#{PYTHON_VERSION}"].opt_bin}/python#{PYTHON_VERSION} #{libexec}/#{pyz} "$@"
    EOS
		(bin/"pdfdateextract").chmod 0755
  end
  test do
	  system "#{bin}/pdfdateextract", "--version"
  end
end
