.intel_syntax noprefix
.global _start

.equ SYS_CLOSE, 3
.equ SYS_NANOSLEEP, 35
.equ SYS_SOCKET, 41
.equ SYS_CONNECT, 42
.equ SYS_ACCEPT, 43
.equ SYS_SENDMSG, 46
.equ SYS_BIND, 49
.equ SYS_LISTEN, 50
.equ SYS_SETSOCKOPT, 54
.equ SYS_EXIT, 60

.equ AF_UNIX, 1
.equ AF_INET, 2
.equ SOCK_STREAM, 1
.equ SOL_SOCKET, 1
.equ SO_REUSEADDR, 2
.equ SCM_RIGHTS, 1
.equ MSG_NOSIGNAL, 0x4000
.equ PORT_9999_BE_WORD, 0x0f27
.equ BACKLOG, 65535

.section .text
_start:
    call connect_api1_forever
    mov qword ptr [rip + upstream1_fd], rax
    call connect_api2_forever
    mov qword ptr [rip + upstream2_fd], rax

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

    mov rax, qword ptr [rip + rr_next]
    xor rax, 1
    mov qword ptr [rip + rr_next], rax
    test rax, rax
    jz use_upstream1

use_upstream2:
    mov rdi, qword ptr [rip + upstream2_fd]
    mov rsi, r13
    call send_fd
    test rax, rax
    jns close_client
    call reconnect_api2_once
    test rax, rax
    js close_client
    mov qword ptr [rip + upstream2_fd], rax
    mov rdi, rax
    mov rsi, r13
    call send_fd
    jmp close_client

use_upstream1:
    mov rdi, qword ptr [rip + upstream1_fd]
    mov rsi, r13
    call send_fd
    test rax, rax
    jns close_client
    call reconnect_api1_once
    test rax, rax
    js close_client
    mov qword ptr [rip + upstream1_fd], rax
    mov rdi, rax
    mov rsi, r13
    call send_fd

close_client:
    mov rax, SYS_CLOSE
    mov rdi, r13
    syscall
    jmp accept_loop

connect_api1_forever:
    lea rdi, [rip + api1_addr]
    mov rsi, OFFSET FLAT:api1_addr_len
    jmp connect_forever

connect_api2_forever:
    lea rdi, [rip + api2_addr]
    mov rsi, OFFSET FLAT:api2_addr_len
    jmp connect_forever

reconnect_api1_once:
    lea rdi, [rip + api1_addr]
    mov rsi, OFFSET FLAT:api1_addr_len
    jmp connect_once

reconnect_api2_once:
    lea rdi, [rip + api2_addr]
    mov rsi, OFFSET FLAT:api2_addr_len
    jmp connect_once

connect_forever:
    push rdi
    push rsi
1:
    mov rdi, [rsp + 8]
    mov rsi, [rsp]
    call connect_once
    test rax, rax
    jns 2f
    lea rdi, [rip + retry_sleep]
    xor rsi, rsi
    mov rax, SYS_NANOSLEEP
    syscall
    jmp 1b
2:
    add rsp, 16
    ret

# rdi = sockaddr_un*, rsi = addrlen; returns fd or negative errno.
connect_once:
    push rdi
    push rsi
    mov rax, SYS_SOCKET
    mov rdi, AF_UNIX
    mov rsi, SOCK_STREAM
    xor rdx, rdx
    syscall
    test rax, rax
    js 9f
    mov rbx, rax
    mov rax, SYS_CONNECT
    mov rdi, rbx
    mov rsi, [rsp + 8]
    mov rdx, [rsp]
    syscall
    test rax, rax
    js 8f
    mov rax, rbx
    add rsp, 16
    ret
8:
    mov rax, SYS_CLOSE
    mov rdi, rbx
    syscall
    mov rax, -1
9:
    add rsp, 16
    ret

# rdi = unix control socket, rsi = client fd. Returns 0 on success, -1 on failure.
send_fd:
    mov qword ptr [rip + iov_base], OFFSET FLAT:send_byte
    mov qword ptr [rip + iov_len], 1
    mov qword ptr [rip + msg_name], 0
    mov qword ptr [rip + msg_namelen], 0
    mov qword ptr [rip + msg_iov], OFFSET FLAT:iov_base
    mov qword ptr [rip + msg_iovlen], 1
    mov qword ptr [rip + msg_control], OFFSET FLAT:cmsg_buf
    mov qword ptr [rip + msg_controllen], 24
    mov qword ptr [rip + msg_flags], 0
    mov qword ptr [rip + cmsg_buf], 20
    mov dword ptr [rip + cmsg_buf + 8], SOL_SOCKET
    mov dword ptr [rip + cmsg_buf + 12], SCM_RIGHTS
    mov dword ptr [rip + cmsg_buf + 16], esi
    mov qword ptr [rip + cmsg_buf + 20], 0

    mov rax, SYS_SENDMSG
    lea rsi, [rip + msg_name]
    mov rdx, MSG_NOSIGNAL
    syscall
    cmp rax, 1
    je 1f
    mov rax, -1
    ret
1:
    xor rax, rax
    ret

fatal:
    mov rax, SYS_EXIT
    mov rdi, 1
    syscall

.section .rodata
retry_sleep:
    .quad 0
    .quad 25000000

api1_addr:
    .word AF_UNIX
    .asciz "/tmp/rinha/api1.sock"
api1_addr_end:
.equ api1_addr_len, api1_addr_end - api1_addr

api2_addr:
    .word AF_UNIX
    .asciz "/tmp/rinha/api2.sock"
api2_addr_end:
.equ api2_addr_len, api2_addr_end - api2_addr

.section .data
send_byte:
    .byte 1

.section .bss
.align 16
sockaddr_in:
    .skip 16
optval:
    .skip 4
upstream1_fd:
    .skip 8
upstream2_fd:
    .skip 8
rr_next:
    .skip 8

.align 8
iov_base:
    .skip 8
iov_len:
    .skip 8
msg_name:
    .skip 8
msg_namelen:
    .skip 8
msg_iov:
    .skip 8
msg_iovlen:
    .skip 8
msg_control:
    .skip 8
msg_controllen:
    .skip 8
msg_flags:
    .skip 8
cmsg_buf:
    .skip 32
