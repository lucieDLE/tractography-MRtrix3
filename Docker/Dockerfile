#FROM dcbia/fly-by-cnn:latest
FROM tensorflow/tensorflow:2.4.1-gpu


RUN apt-get update && apt-get install -y \
	git \
	libx11-6 \
	libgl1 \
	libopengl0 \
	libegl1 \
	wget



RUN pip install itk sklearn pandas matplotlib nibabel
RUN pip install tqdm tensorflow_datasets tensorflow_probability plotly seaborn

RUN wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
RUN bash Anaconda3-5.0.1-Linux-x86_64.sh -b
RUN rm Anaconda3-5.0.1-Linux-x86_64.sh

# Set path to conda
ENV PATH /root/anaconda3/bin:$PATH

RUN conda install -c mrtrix3 mrtrix3 


WORKDIR /usr/local/lib/python3.6/dist-packages/

RUN wget https://github.com/DCBIA-OrthoLab/fly-by-cnn/releases/download/2.0/vtk8.2.0.zip
RUN	unzip vtk8.2.0.zip


WORKDIR /app

RUN git clone https://github.com/lucieDLE/fly-by-cnn.git
RUN git clone https://github.com/ahsanMah/msma.git
RUN git clone https://github.com/lucieDLE/tractography-mrtrix.git



ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/python3.6/dist-packages/vtkmodules/
ENV MESA_GL_VERSION_OVERRIDE=3.2