FROM gcc:latest AS build
ARG PROJECT_DIR

WORKDIR /app

COPY src/ ./src/
COPY CMakeLists.txt .

WORKDIR /app/build

RUN cmake -DCMAKE_BUILD_TYPE=Release .. && \
    cmake --build . \

FROM alpine:3.17.0
RUN addgroup -S user && adduser -S user -G user
USER user

COPY --chown=user:user --from=build \
    ./app/build/$PROJECT_DIR \
    ./app/

ENTRYPOINT [ "./app" ]