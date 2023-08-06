from setuptools import setup

setup(
    name="sspqdd",
    version="1.0.4",
    description="Single-Shot-Power-Quality-Disturbance-Detector",
    author="Carlos Iturrino-García",
    author_email="carlos.iturrino.garcia@gmail.com",
    packages=["sspqdd"],
    long_description = "Single-Shot-Power-Quality-Disturbance-Detector (SSPQDD) is a Python package that provides a "
                       "comprehensive solution for detection and"
                       " classification of power quality disturbances. It utilizes state-of-the-art deep learning "
                       "algorithms to analyze power signals and identify various types of disturbances, such as voltage"
                       "sags, swells, harmonics, transients, notch and interruptions. The SSPQDD is designed to empower"
                       " engineers and researchers working in the field of power quality analysis. By leveraging "
                       "deep learning techniques, it offers an efficient and accurate approach to automatically detect "
                       "and classify power disturbances, saving time and effort compared to manual inspection. "
                       "With the SSPQDD, users can gain valuable insights into power quality issues and make informed "
                       "decisions for optimal system performance and reliability. \n Features: \n "
                       "- Detection and "
                       "classification of power quality disturbances: SSPQDD provides an extensive library of "
                       "pre-trained deep learning models capable of identifying various power disturbances ",
                       # "with high precision. \n - Real-time monitoring: It enables real-time analysis of power signals,"
                       # "allowing for immediate detection and notification of disturbances as they occur.\n "
                       # "-Customizability: Users have the flexibility to fine-tune or retrain the models with their "
                       # "own datasets to cater to specific power quality analysis requirements. \n"
                       # "-Visualization and reporting: PowerQDetect offers interactive visualization "
                       # "tools and comprehensive reporting capabilities to help users interpret the detected disturbances "
                       # "and generate detailed reports.",
    # install_requires=[
    #     "numpy",
    #     "pandas",
    # ],
)