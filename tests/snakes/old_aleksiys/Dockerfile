FROM walberla/buildenv-ubuntu-gcc:7

RUN mkdir -p /code
WORKDIR /code
RUN git clone https://github.com/rdbrck/battlesnake-2017-aleksiys-snake.git .
RUN git submodule init
RUN git submodule sync
RUN git submodule update
WORKDIR /code/crow
RUN git checkout 7560f329c90fe3d9777ad41cdcbb94b1a67986b8
WORKDIR /code

RUN make

EXPOSE 9001

CMD ["make", "run"]