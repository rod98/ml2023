FROM python:3.11.3-slim-bullseye

RUN echo "en_GB.UTF-8 UTF-8" >  /etc/locale.gen
RUN echo "ru_RU.UTF-8 UTF-8" >> /etc/locale.gen
RUN echo LANG="en_GB.UTF-8"  >  /etc/locale.conf

RUN apt update
RUN apt -y install locales
RUN locale-gen
RUN apt clean

RUN useradd -m backadm

COPY --chown=backadm:backadm requirements.txt /home/backadm/requirements.txt
RUN python3 -m pip install -r /home/backadm/requirements.txt
RUN pip cache remove '*'

USER backadm

COPY src/ /home/backadm/src

ENV PATH=/home/backadm/.local/bin:$PATH
ENV PYTHONPATH=$PYTHONPATH:/home/backadm/src

RUN echo 'export PS1="\[\e[1;32m\]\w\[\e[1;33m\] \$ \[\e[0m\]"' >> ~/.bashrc

WORKDIR /home/backadm

EXPOSE 8000
ENTRYPOINT ["python3", "-m", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0"]
