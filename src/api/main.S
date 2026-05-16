.intel_syntax noprefix
.global _start

.equ SYS_READ, 0
.equ SYS_WRITE, 1
.equ SYS_CLOSE, 3
.equ SYS_SOCKET, 41
.equ SYS_ACCEPT, 43
.equ SYS_BIND, 49
.equ SYS_LISTEN, 50
.equ SYS_SETSOCKOPT, 54
.equ SYS_EXIT, 60

.equ AF_INET, 2
.equ SOCK_STREAM, 1
.equ SOL_SOCKET, 1
.equ SO_REUSEADDR, 2
.equ PORT_9999_BE_WORD, 0x0f27
.equ BACKLOG, 4096
.equ BUF_SIZE, 4096

.section .text
_start:
    mov rax, SYS_SOCKET
    mov rdi, AF_INET
    mov rsi, SOCK_STREAM
    xor rdx, rdx
    syscall
    test rax, rax
    js fatal
    mov r12, rax

    mov dword ptr [rip + optval], 1
    mov rax, SYS_SETSOCKOPT
    mov rdi, r12
    mov rsi, SOL_SOCKET
    mov rdx, SO_REUSEADDR
    lea r10, [rip + optval]
    mov r8, 4
    syscall

    mov word ptr [rip + sockaddr_in], AF_INET
    mov word ptr [rip + sockaddr_in + 2], PORT_9999_BE_WORD
    mov dword ptr [rip + sockaddr_in + 4], 0
    mov qword ptr [rip + sockaddr_in + 8], 0

    mov rax, SYS_BIND
    mov rdi, r12
    lea rsi, [rip + sockaddr_in]
    mov rdx, 16
    syscall
    test rax, rax
    js fatal

    mov rax, SYS_LISTEN
    mov rdi, r12
    mov rsi, BACKLOG
    syscall
    test rax, rax
    js fatal

accept_loop:
    mov rax, SYS_ACCEPT
    mov rdi, r12
    xor rsi, rsi
    xor rdx, rdx
    syscall
    test rax, rax
    js accept_loop
    mov r13, rax

    mov rax, SYS_READ
    mov rdi, r13
    lea rsi, [rip + request_buffer]
    mov rdx, BUF_SIZE
    syscall
    test rax, rax
    jle close_client

    cmp dword ptr [rip + request_buffer], 0x20544547    # "GET "
    je write_ready
    cmp dword ptr [rip + request_buffer], 0x54534f50    # "POST"
    je write_fraud_default
    jmp write_not_found

write_ready:
    lea rsi, [rip + ready_response]
    mov rdx, OFFSET FLAT:ready_response_len
    jmp write_response

write_fraud_default:
    lea rsi, [rip + fraud0_response]
    mov rdx, OFFSET FLAT:fraud0_response_len
    jmp write_response

write_not_found:
    lea rsi, [rip + not_found_response]
    mov rdx, OFFSET FLAT:not_found_response_len

write_response:
    mov rax, SYS_WRITE
    mov rdi, r13
    syscall

close_client:
    mov rax, SYS_CLOSE
    mov rdi, r13
    syscall
    jmp accept_loop

fatal:
    mov rax, SYS_EXIT
    mov rdi, 1
    syscall

.section .rodata
ready_response:
    .ascii "HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nOK"
.equ ready_response_len, . - ready_response

fraud0_response:
    .ascii "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 36\r\nConnection: close\r\n\r\n{\"approved\":true,\"fraud_score\":0.0}"
.equ fraud0_response_len, . - fraud0_response

not_found_response:
    .ascii "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
.equ not_found_response_len, . - not_found_response

.section .bss
.align 16
request_buffer:
    .skip BUF_SIZE
sockaddr_in:
    .skip 16
optval:
    .skip 4
