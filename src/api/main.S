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

    lea rdi, [rip + request_buffer]
    xor eax, eax
    mov ecx, BUF_SIZE / 8
    rep stosq

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
    call choose_fraud_response
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
    lea rdi, [rip + request_buffer]
    xor eax, eax
    mov ecx, BUF_SIZE / 8
    rep stosq

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
    call choose_fraud_response
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

# Test-backed assembly scorer increment. It still is not the final nearest-
# vector search from the C participant, but it now parses multiple official
# JSON fields and maps a capped fraud-count to every public response bucket.
choose_fraud_response:
    xor r11d, r11d

    call tx_count_value
    cmp eax, 20
    jae score_tx_high
    cmp eax, 10
    jb score_amount
    inc r11d
    jmp score_amount
score_tx_high:
    add r11d, 2

score_amount:
    call amount_value
    mov r10d, eax
    cmp eax, 10000
    jb score_installments
    inc r11d

score_installments:
    call installments_value
    cmp eax, 10
    jb score_online
    inc r11d

score_online:
    call is_online_value
    test eax, eax
    jz score_card_present
    inc r11d

score_card_present:
    call card_present_value
    test eax, eax
    jnz score_avg_ratio
    inc r11d

score_avg_ratio:
    call avg_amount_value
    test eax, eax
    jz score_km_home
    imul eax, eax, 5
    cmp r10d, eax
    jb score_km_home
    inc r11d

score_km_home:
    call km_from_home_value
    cmp eax, 500
    jb score_mcc
    inc r11d

score_mcc:
    call mcc_risk_value
    test eax, eax
    jz score_known_merchant
    inc r11d

score_known_merchant:
    call merchant_unknown_value
    test eax, eax
    jz score_requested_hour
    inc r11d

score_requested_hour:
    call requested_hour_value
    cmp eax, 6
    jb score_requested_hour_risky
    cmp eax, 22
    jb score_last_recent
score_requested_hour_risky:
    inc r11d

score_last_recent:
    call last_recent_value
    test eax, eax
    jz score_km_current
    inc r11d

score_km_current:
    call km_from_current_value
    cmp eax, 500
    jb score_dispatch
    inc r11d

score_dispatch:
    cmp r11d, 5
    jbe score_dispatch_capped
    mov r11d, 5
score_dispatch_capped:
    cmp r11d, 0
    je choose_fraud0
    cmp r11d, 1
    je choose_fraud1
    cmp r11d, 2
    je choose_fraud2
    cmp r11d, 3
    je choose_fraud3
    cmp r11d, 4
    je choose_fraud4
    jmp choose_fraud5
choose_fraud0:
    lea rsi, [rip + fraud0_response]
    mov rdx, OFFSET FLAT:fraud0_response_len
    ret
choose_fraud1:
    lea rsi, [rip + fraud1_response]
    mov rdx, OFFSET FLAT:fraud1_response_len
    ret
choose_fraud2:
    lea rsi, [rip + fraud2_response]
    mov rdx, OFFSET FLAT:fraud2_response_len
    ret
choose_fraud3:
    lea rsi, [rip + fraud3_response]
    mov rdx, OFFSET FLAT:fraud3_response_len
    ret
choose_fraud4:
    lea rsi, [rip + fraud4_response]
    mov rdx, OFFSET FLAT:fraud4_response_len
    ret
choose_fraud5:
    lea rsi, [rip + fraud5_response]
    mov rdx, OFFSET FLAT:fraud5_response_len
    ret

amount_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 10
find_amount_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x22746e756f6d6122
    cmp rax, r9                         # "amount"
    je found_amount_key
    inc r8
    dec ecx
    jnz find_amount_key
    xor rax, rax
    ret
found_amount_key:
    add r8, 8
    jmp parse_number_after_key

avg_amount_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 14
find_avg_amount_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x6f6d615f67766122
    cmp rax, r9                         # "avg_amo
    jne next_avg_amount_byte
    cmp dword ptr [r8 + 8], 0x22746e75  # unt"
    je found_avg_amount_key
next_avg_amount_byte:
    inc r8
    dec ecx
    jnz find_avg_amount_key
    xor rax, rax
    ret
found_avg_amount_key:
    add r8, 12
    jmp parse_number_after_key

installments_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 16
find_installments_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x6c6c6174736e6922
    cmp rax, r9                         # "install
    jne next_installments_byte
    cmp dword ptr [r8 + 8], 0x746e656d  # ment
    jne next_installments_byte
    cmp word ptr [r8 + 12], 0x2273      # s"
    je found_installments_key
next_installments_byte:
    inc r8
    dec ecx
    jnz find_installments_key
    xor rax, rax
    ret
found_installments_key:
    add r8, 14
    jmp parse_number_after_key

is_online_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 13
find_online_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x696c6e6f5f736922
    cmp rax, r9                         # "is_onli
    jne next_online_byte
    cmp word ptr [r8 + 8], 0x656e       # ne
    jne next_online_byte
    cmp byte ptr [r8 + 10], '"'
    je found_online_key
next_online_byte:
    inc r8
    dec ecx
    jnz find_online_key
    xor rax, rax
    ret
found_online_key:
    add r8, 11
    jmp parse_bool_after_key

card_present_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 16
find_card_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x72705f6472616322
    cmp rax, r9                         # "card_pr
    jne next_card_byte
    cmp dword ptr [r8 + 8], 0x6e657365  # esen
    jne next_card_byte
    cmp word ptr [r8 + 12], 0x2274      # t"
    je found_card_key
next_card_byte:
    inc r8
    dec ecx
    jnz find_card_key
    xor rax, rax
    ret
found_card_key:
    add r8, 14
    jmp parse_bool_after_key

km_from_home_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 16
find_km_home_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x6d6f72665f6d6b22
    cmp rax, r9                         # "km_from
    jne next_km_home_byte
    cmp dword ptr [r8 + 8], 0x6d6f685f  # _hom
    jne next_km_home_byte
    cmp word ptr [r8 + 12], 0x2265      # e"
    jne next_km_home_byte
    jmp found_km_home_key
next_km_home_byte:
    inc r8
    dec ecx
    jnz find_km_home_key
    xor rax, rax
    ret
found_km_home_key:
    add r8, 14
    jmp parse_number_after_key

mcc_risk_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 8
find_mcc_key:
    cmp dword ptr [r8], 0x63636d22      # "mcc
    jne next_mcc_byte
    cmp byte ptr [r8 + 4], '"'
    je found_mcc_key
next_mcc_byte:
    inc r8
    dec ecx
    jnz find_mcc_key
    xor rax, rax
    ret
found_mcc_key:
    add r8, 5
    mov ecx, 64
find_mcc_colon:
    cmp byte ptr [r8], ':'
    je found_mcc_colon
    inc r8
    dec ecx
    jnz find_mcc_colon
    xor rax, rax
    ret
found_mcc_colon:
    inc r8
skip_mcc_ws:
    mov al, byte ptr [r8]
    cmp al, ' '
    je advance_mcc_ws
    cmp al, 9
    je advance_mcc_ws
    cmp al, '"'
    je advance_mcc_ws
    jmp check_mcc_risk
advance_mcc_ws:
    inc r8
    jmp skip_mcc_ws
check_mcc_risk:
    cmp dword ptr [r8], 0x35393937      # 7995
    je parsed_mcc_risk
    xor rax, rax
    ret
parsed_mcc_risk:
    mov eax, 1
    ret

merchant_unknown_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 20
find_known_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x6d5f6e776f6e6b22
    cmp rax, r9                         # "known_m
    jne next_known_byte
    mov rax, qword ptr [r8 + 8]
    movabs r9, 0x73746e6168637265
    cmp rax, r9                         # erchants
    jne next_known_byte
    cmp byte ptr [r8 + 16], '"'
    je found_known_key
next_known_byte:
    inc r8
    dec ecx
    jnz find_known_key
    xor rax, rax
    ret
found_known_key:
    add r8, 17
find_known_open:
    cmp byte ptr [r8], '['
    je found_known_open
    inc r8
    jmp find_known_open
found_known_open:
    mov r9, r8                          # known array start
find_known_close:
    cmp byte ptr [r8], ']'
    je found_known_close
    inc r8
    jmp find_known_close
found_known_close:
    mov r10, r8                         # known array end
    mov r8, r10
    mov ecx, 512
find_merchant_id_prefix:
    cmp dword ptr [r8], 0x4352454d      # MERC
    jne next_merchant_id_prefix
    cmp byte ptr [r8 + 4], '-'
    je found_merchant_id_prefix
next_merchant_id_prefix:
    inc r8
    dec ecx
    jnz find_merchant_id_prefix
    xor rax, rax
    ret
found_merchant_id_prefix:
    mov edx, dword ptr [r8 + 5]         # three digits plus closing quote
    mov r8, r9
scan_known_for_id:
    cmp r8, r10
    jae merchant_id_unknown
    cmp dword ptr [r8], edx
    je merchant_id_known
    inc r8
    jmp scan_known_for_id
merchant_id_known:
    xor rax, rax
    ret
merchant_id_unknown:
    mov eax, 1
    ret

requested_hour_value:
    call requested_at_value_ptr
    test rax, rax
    jz requested_hour_missing
    movzx eax, byte ptr [r8 + 11]
    sub eax, '0'
    imul eax, eax, 10
    movzx edx, byte ptr [r8 + 12]
    sub edx, '0'
    add eax, edx
    ret
requested_hour_missing:
    mov eax, 12
    ret

requested_at_value_ptr:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 16
find_requested_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x7473657571657222
    cmp rax, r9                         # "request
    jne next_requested_byte
    cmp dword ptr [r8 + 8], 0x615f6465  # ed_a
    jne next_requested_byte
    cmp word ptr [r8 + 12], 0x2274      # t"
    je found_requested_key
next_requested_byte:
    inc r8
    dec ecx
    jnz find_requested_key
    xor rax, rax
    ret
found_requested_key:
    add r8, 14
    jmp parse_string_after_key

timestamp_value_ptr:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 13
find_timestamp_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x617473656d697422
    cmp rax, r9                         # "timesta
    jne next_timestamp_byte
    cmp word ptr [r8 + 8], 0x706d       # mp
    jne next_timestamp_byte
    cmp byte ptr [r8 + 10], '"'
    je found_timestamp_key
next_timestamp_byte:
    inc r8
    dec ecx
    jnz find_timestamp_key
    xor rax, rax
    ret
found_timestamp_key:
    add r8, 11
    jmp parse_string_after_key

last_recent_value:
    call requested_at_value_ptr
    test rax, rax
    jz last_recent_no
    movzx eax, byte ptr [r8 + 8]
    sub eax, '0'
    imul eax, eax, 10
    movzx edx, byte ptr [r8 + 9]
    sub edx, '0'
    add eax, edx
    imul eax, eax, 1440
    mov r10d, eax
    movzx eax, byte ptr [r8 + 11]
    sub eax, '0'
    imul eax, eax, 10
    movzx edx, byte ptr [r8 + 12]
    sub edx, '0'
    add eax, edx
    imul eax, eax, 60
    add r10d, eax
    movzx eax, byte ptr [r8 + 14]
    sub eax, '0'
    imul eax, eax, 10
    movzx edx, byte ptr [r8 + 15]
    sub edx, '0'
    add eax, edx
    add r10d, eax

    call timestamp_value_ptr
    test rax, rax
    jz last_recent_no
    movzx eax, byte ptr [r8 + 8]
    sub eax, '0'
    imul eax, eax, 10
    movzx edx, byte ptr [r8 + 9]
    sub edx, '0'
    add eax, edx
    imul eax, eax, 1440
    mov r9d, eax
    movzx eax, byte ptr [r8 + 11]
    sub eax, '0'
    imul eax, eax, 10
    movzx edx, byte ptr [r8 + 12]
    sub edx, '0'
    add eax, edx
    imul eax, eax, 60
    add r9d, eax
    movzx eax, byte ptr [r8 + 14]
    sub eax, '0'
    imul eax, eax, 10
    movzx edx, byte ptr [r8 + 15]
    sub edx, '0'
    add eax, edx
    add r9d, eax

    mov eax, r10d
    sub eax, r9d
    cmp eax, 0
    jl last_recent_no
    cmp eax, 10
    jg last_recent_no
    mov eax, 1
    ret
last_recent_no:
    xor rax, rax
    ret

km_from_current_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 20
find_km_current_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x6d6f72665f6d6b22
    cmp rax, r9                         # "km_from
    jne next_km_current_byte
    mov rax, qword ptr [r8 + 8]
    movabs r9, 0x746e65727275635f
    cmp rax, r9                         # _current
    jne next_km_current_byte
    cmp byte ptr [r8 + 16], '"'
    je found_km_current_key
next_km_current_byte:
    inc r8
    dec ecx
    jnz find_km_current_key
    xor rax, rax
    ret
found_km_current_key:
    add r8, 17
    jmp parse_number_after_key

tx_count_value:
    lea r8, [rip + request_buffer]
    mov ecx, BUF_SIZE - 16
find_tx_key:
    mov rax, qword ptr [r8]
    movabs r9, 0x6e756f635f787422
    cmp rax, r9     # "tx_coun
    jne next_tx_byte
    cmp dword ptr [r8 + 8], 0x34325f74         # t_24
    jne next_tx_byte
    cmp word ptr [r8 + 12], 0x2268             # h"
    je found_tx_key
next_tx_byte:
    inc r8
    dec ecx
    jnz find_tx_key
    xor rax, rax
    ret

found_tx_key:
    add r8, 14

parse_number_after_key:
    mov ecx, 64
find_tx_colon:
    cmp byte ptr [r8], ':'
    je found_tx_colon
    inc r8
    dec ecx
    jnz find_tx_colon
    xor rax, rax
    ret
found_tx_colon:
    inc r8
skip_tx_ws:
    mov al, byte ptr [r8]
    cmp al, ' '
    je advance_tx_ws
    cmp al, 9
    je advance_tx_ws
    cmp al, 10
    je advance_tx_ws
    cmp al, 13
    je advance_tx_ws
    jmp parse_tx_digits
advance_tx_ws:
    inc r8
    jmp skip_tx_ws
parse_tx_digits:
    xor ebx, ebx
parse_tx_loop:
    movzx eax, byte ptr [r8]
    cmp al, '0'
    jb parsed_tx_count
    cmp al, '9'
    ja parsed_tx_count
    imul ebx, ebx, 10
    sub eax, '0'
    add ebx, eax
    inc r8
    jmp parse_tx_loop
parsed_tx_count:
    mov eax, ebx
    ret

parse_bool_after_key:
    mov ecx, 64
find_bool_colon:
    cmp byte ptr [r8], ':'
    je found_bool_colon
    inc r8
    dec ecx
    jnz find_bool_colon
    xor rax, rax
    ret
found_bool_colon:
    inc r8
skip_bool_ws:
    mov al, byte ptr [r8]
    cmp al, ' '
    je advance_bool_ws
    cmp al, 9
    je advance_bool_ws
    cmp al, 10
    je advance_bool_ws
    cmp al, 13
    je advance_bool_ws
    jmp parse_bool_literal
advance_bool_ws:
    inc r8
    jmp skip_bool_ws
parse_bool_literal:
    cmp dword ptr [r8], 0x65757274      # true
    je parsed_bool_true
    xor rax, rax
    ret
parsed_bool_true:
    mov eax, 1
    ret

parse_string_after_key:
    mov ecx, 64
find_string_colon:
    cmp byte ptr [r8], ':'
    je found_string_colon
    inc r8
    dec ecx
    jnz find_string_colon
    xor rax, rax
    ret
found_string_colon:
    inc r8
skip_string_ws:
    mov al, byte ptr [r8]
    cmp al, ' '
    je advance_string_ws
    cmp al, 9
    je advance_string_ws
    cmp al, 10
    je advance_string_ws
    cmp al, 13
    je advance_string_ws
    cmp al, '"'
    je found_string_quote
    xor rax, rax
    ret
advance_string_ws:
    inc r8
    jmp skip_string_ws
found_string_quote:
    inc r8
    mov rax, r8
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
    .ascii "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 35\r\nConnection: close\r\n\r\n{\"approved\":true,\"fraud_score\":0.0}"
.equ fraud0_response_len, . - fraud0_response

fraud1_response:
    .ascii "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 35\r\nConnection: close\r\n\r\n{\"approved\":true,\"fraud_score\":0.2}"
.equ fraud1_response_len, . - fraud1_response

fraud2_response:
    .ascii "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 35\r\nConnection: close\r\n\r\n{\"approved\":true,\"fraud_score\":0.4}"
.equ fraud2_response_len, . - fraud2_response

fraud3_response:
    .ascii "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 36\r\nConnection: close\r\n\r\n{\"approved\":false,\"fraud_score\":0.6}"
.equ fraud3_response_len, . - fraud3_response

fraud4_response:
    .ascii "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 36\r\nConnection: close\r\n\r\n{\"approved\":false,\"fraud_score\":0.8}"
.equ fraud4_response_len, . - fraud4_response

fraud5_response:
    .ascii "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 36\r\nConnection: close\r\n\r\n{\"approved\":false,\"fraud_score\":1.0}"
.equ fraud5_response_len, . - fraud5_response

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
