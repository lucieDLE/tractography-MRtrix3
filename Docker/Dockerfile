#FROM dcbia/fly-by-cnn:latest
FROM msma:version1


RUN apt-get update && apt-get install -y \
	git \
	libx11-6 \
	libgl1 \
	libopengl0 \
	libegl1 \
	wget

WORKDIR /usr/local/lib/python3.6/dist-packages/

RUN wget https://github.com/DCBIA-OrthoLab/fly-by-cnn/releases/download/2.0/vtk8.2.0.zip
RUN	unzip vtk8.2.0.zip

RUN pip install itk sklearn pandas matplotlib

#RUN pip install tqdm tensorflow_datasets tensorflow_probability plotly seaborn tensorflow_addons
RUN pip install nibabel

#RUN conda install -c mrtrix3 mrtrix3 

WORKDIR /app

RUN git clone https://github.com/lucieDLE/fly-by-cnn.git
RUN git clone https://github.com/ahsanMah/msma.git
RUN git clone https://github.com/lucieDLE/tractography-mrtrix.git



ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/python3.6/dist-packages/vtkmodules/
ENV MESA_GL_VERSION_OVERRIDE=3.2
