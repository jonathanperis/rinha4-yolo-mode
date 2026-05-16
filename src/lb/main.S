.intel_syntax noprefix
.global _start

.equ SYS_WRITE, 1
.equ SYS_EXIT, 60

.section .text
_start:
    # Placeholder binary while the fd-passing load balancer is ported from
    # rinha4-lb-yolo-mode C to pure x86-64 assembly. It intentionally does not
    # proxy or inspect traffic yet, so this repository is not submission-ready.
    mov rax, SYS_WRITE
    mov rdi, 2
    lea rsi, [rip + msg]
    mov rdx, msg_len
    syscall

    mov rax, SYS_EXIT
    mov rdi, 78
    syscall

.section .rodata
msg:
    .ascii "asm lb scaffold: fdpass implementation pending\n"
.equ msg_len, . - msg
