.intel_syntax noprefix
.global _start

.equ SYS_READ, 0
.equ SYS_WRITE, 1
.equ SYS_CLOSE, 3
.equ SYS_SOCKET, 41
.equ SYS_ACCEPT, 43
.equ SYS_RECVMSG, 47
.equ SYS_BIND, 49
.equ SYS_LISTEN, 50
.equ SYS_SETSOCKOPT, 54
.equ SYS_EXIT, 60
.equ SYS_UNLINK, 87

.equ AF_UNIX, 1
.equ AF_INET, 2
.equ SOCK_STREAM, 1
.equ SOL_SOCKET, 1
.equ SO_REUSEADDR, 2
.equ SCM_RIGHTS, 1
.equ PORT_9999_BE_WORD, 0x0f27
.equ BACKLOG, 4096
.equ BUF_SIZE, 4096

.section .text
_start:
    mov rbx, rsp
    mov rax, qword ptr [rbx]
    cmp rax, 2
    jb direct_tcp_start
    mov rdi, qword ptr [rbx + 16]
    jmp unix_fdpass_start

direct_tcp_start:
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

unix_fdpass_start:
    # argv[1] is the Unix-domain control socket path. The LB sends accepted
    # client sockets over this connection with SCM_RIGHTS.
    mov r14, rdi
    mov rax, SYS_UNLINK
    mov rdi, r14
    syscall

    mov rax, SYS_SOCKET
    mov rdi, AF_UNIX
    mov rsi, SOCK_STREAM
    xor rdx, rdx
    syscall
    test rax, rax
    js fatal
    mov r12, rax

    mov word ptr [rip + sockaddr_un], AF_UNIX
    lea rdi, [rip + sockaddr_un + 2]
    mov rsi, r14
    mov rcx, 107
copy_unix_path:
    lodsb
    stosb
    test al, al
    jz copied_unix_path
    loop copy_unix_path
    mov byte ptr [rdi], 0
copied_unix_path:
    mov rax, SYS_BIND
    mov rdi, r12
    lea rsi, [rip + sockaddr_un]
    mov rdx, 110
    syscall
    test rax, rax
    js fatal

    mov rax, SYS_LISTEN
    mov rdi, r12
    mov rsi, 128
    syscall
    test rax, rax
    js fatal

ctrl_accept_loop:
    mov rax, SYS_ACCEPT
    mov rdi, r12
    xor rsi, rsi
    xor rdx, rdx
    syscall
    test rax, rax
    js ctrl_accept_loop
    mov r15, rax

recv_fd_loop:
    call recv_client_fd
    test rax, rax
    js close_ctrl
    mov r13, rax
    call fdpass_process_client
    jmp recv_fd_loop

close_ctrl:
    mov rax, SYS_CLOSE
    mov rdi, r15
    syscall
    jmp ctrl_accept_loop

recv_client_fd:
    mov qword ptr [rip + recv_iov_base], OFFSET FLAT:recv_byte
    mov qword ptr [rip + recv_iov_len], 1
    mov qword ptr [rip + recv_msg_name], 0
    mov qword ptr [rip + recv_msg_namelen], 0
    mov qword ptr [rip + recv_msg_iov], OFFSET FLAT:recv_iov_base
    mov qword ptr [rip + recv_msg_iovlen], 1
    mov qword ptr [rip + recv_msg_control], OFFSET FLAT:recv_cmsg_buf
    mov qword ptr [rip + recv_msg_controllen], 24
    mov qword ptr [rip + recv_msg_flags], 0

    mov rax, SYS_RECVMSG
    mov rdi, r15
    lea rsi, [rip + recv_msg_name]
    xor rdx, rdx
    syscall
    cmp rax, 1
    jl recv_fd_fail
    cmp dword ptr [rip + recv_cmsg_buf + 8], SOL_SOCKET
    jne recv_fd_fail
    cmp dword ptr [rip + recv_cmsg_buf + 12], SCM_RIGHTS
    jne recv_fd_fail
    mov eax, dword ptr [rip + recv_cmsg_buf + 16]
    ret
recv_fd_fail:
    mov rax, -1
    ret

fdpass_process_client:
    mov rax, SYS_READ
    mov rdi, r13
    lea rsi, [rip + request_buffer]
    mov rdx, BUF_SIZE
    syscall
    test rax, rax
    jle fdpass_close_client

    cmp dword ptr [rip + request_buffer], 0x20544547    # "GET "
    je fdpass_write_ready
    cmp dword ptr [rip + request_buffer], 0x54534f50    # "POST"
    je fdpass_write_fraud_default
    jmp fdpass_write_not_found

fdpass_write_ready:
    lea rsi, [rip + ready_response]
    mov rdx, OFFSET FLAT:ready_response_len
    jmp fdpass_write_response

fdpass_write_fraud_default:
    lea rsi, [rip + fraud0_response]
    mov rdx, OFFSET FLAT:fraud0_response_len
    jmp fdpass_write_response

fdpass_write_not_found:
    lea rsi, [rip + not_found_response]
    mov rdx, OFFSET FLAT:not_found_response_len

fdpass_write_response:
    mov rax, SYS_WRITE
    mov rdi, r13
    syscall

fdpass_close_client:
    mov rax, SYS_CLOSE
    mov rdi, r13
    syscall
    ret

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
sockaddr_un:
    .skip 110
recv_byte:
    .skip 1
.align 8
recv_iov_base:
    .skip 8
recv_iov_len:
    .skip 8
recv_msg_name:
    .skip 8
recv_msg_namelen:
    .skip 8
recv_msg_iov:
    .skip 8
recv_msg_iovlen:
    .skip 8
recv_msg_control:
    .skip 8
recv_msg_controllen:
    .skip 8
recv_msg_flags:
    .skip 8
recv_cmsg_buf:
    .skip 32
