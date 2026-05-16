FROM alpine:3.20 AS build
RUN apk add --no-cache binutils make
WORKDIR /src
COPY . .
RUN make clean all

FROM alpine:3.20
WORKDIR /app
COPY --from=build /src/build/api /app/api
CMD ["/app/api"]
