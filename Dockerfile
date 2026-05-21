ARG ALPINE_VERSION=3.20

FROM alpine:${ALPINE_VERSION} AS build
RUN apk add --no-cache binutils make
WORKDIR /src
COPY . .
RUN make clean all

FROM alpine:${ALPINE_VERSION}
WORKDIR /app
COPY --from=build /src/build/api /app/api
EXPOSE 9999
CMD ["/app/api"]
