#!/bin/bash
# ทดสอบความทนทานของ sched_profiler (คนที่ 2) ตามที่ reviewer ขอ
# รันจากโฟลเดอร์ repo ที่ make แล้ว:
#   sudo bash evidence/05-probe-switch/robustness_test.sh | tee robustness-result.txt
# แนะนำ: snapshot VM ก่อนรัน

P=/proc/sched_profiler
KO=./sched_profiler.ko
pass=0; fail=0
ok() { echo "PASS: $1"; pass=$((pass+1)); }
ng() { echo "FAIL: $1"; fail=$((fail+1)); }
wr() { { echo "$1" > $P; } 2>&1; }          # คืนข้อความ error (ถ้ามี)
val() { awk -v k="$1:" '$1==k{print $2}' $P; }

[ "$(id -u)" = 0 ] || { echo "ต้องรันด้วย sudo"; exit 1; }
[ -f $KO ] || { echo "ไม่พบ $KO (ต้อง make ก่อน)"; exit 1; }
uname -r
lsmod | grep -q '^sched_profiler' && rmmod sched_profiler
n0=$(dmesg | wc -l)

yes > /dev/null & A=$!
yes > /dev/null & B=$!
sleep 1000 & S=$!
sleep 1

echo "== 1. อ่านก่อน start ต้องได้ ENODATA (-61)"
insmod $KO
out=$(cat $P); echo "$out"
[[ "$out" == *"-61"* ]] && ok "read before start" || ng "read before start"

echo "== 2. input ผิด"
m=$(wr abc);      echo "abc      -> $m"; [[ "$m" == *"Invalid argument"* ]] && ok "abc -> EINVAL" || ng "abc"
m=$(wr -5);       echo "-5       -> $m"; [[ "$m" == *"Invalid argument"* ]] && ok "-5 -> EINVAL" || ng "-5"
m=$(wr 99999999); echo "99999999 -> $m"; [[ "$m" == *"No such process"* ]] && ok "99999999 -> ESRCH" || ng "99999999"

echo "== 3. start ซ้อน ต้องได้ EBUSY"
wr $A
m=$(wr $B); echo "start $B ขณะวัด $A -> $m"
[[ "$m" == *"busy"* ]] && ok "double start -> EBUSY" || ng "double start"

echo "== 4. stop แล้วต้องหยุดนับ"
sleep 2; wr 0
r1=$(val switch_out); sleep 3; r2=$(val switch_out)
echo "switch_out หลัง stop: $r1 -> (3 วินาที) -> $r2"
[ -n "$r1" ] && [ "$r1" -gt 0 ] && [ "$r1" = "$r2" ] && ok "stop freezes counters" || ng "stop freezes counters"

echo "== 5. start ใหม่ ตัวนับต้องเริ่มจาก 0"
wr $A; r3=$(val switch_out); wr 0
echo "รอบก่อน $r1, ทันทีหลัง start ใหม่ $r3"
[ "$r3" -lt 10 ] && [ "$r3" -lt "$r1" ] && ok "counters reset on start" || ng "counters reset on start"

echo "== 6. ไม่นับ PID อื่น (เฝ้า sleep ที่หลับอยู่ ขณะ yes 2 ตัวรันเต็ม CPU)"
wr $S; sleep 3; wr 0; cat $P
[ "$(val switch_in)" = 0 ] && [ "$(val switch_out)" = 0 ] && ok "only target pid counted" || ng "only target pid counted"

echo "== (ก) rmmod ขณะกำลังวัด (ไม่ stop ก่อน)"
wr $A; sleep 1
rmmod sched_profiler && ok "rmmod while measuring" || ng "rmmod while measuring"

echo "== (ข) insmod -> start -> stop -> rmmod 10 รอบ"
loopfail=0
for i in $(seq 1 10); do
	insmod $KO && [ -z "$(wr $A)" ] && sleep 1 && [ -z "$(wr 0)" ] \
		&& echo "  รอบ $i: switch_out=$(val switch_out)" && rmmod sched_profiler \
		|| { echo "  รอบ $i: FAIL"; loopfail=1; lsmod | grep -q '^sched_profiler' && rmmod sched_profiler; }
done
[ $loopfail = 0 ] && ok "10 load/unload cycles" || ng "10 load/unload cycles"

kill $A $B $S 2>/dev/null

echo "== dmesg ระหว่างทดสอบ"
dmesg | tail -n +$((n0+1)) | grep sched_profiler | tail -8
bad=$(dmesg | tail -n +$((n0+1)) | grep -Ei 'oops|bug:|warning:|call trace|panic')
[ -z "$bad" ] && ok "dmesg clean (no oops/BUG/WARNING)" || { echo "$bad"; ng "dmesg clean"; }

echo "== สรุป: PASS $pass  FAIL $fail"
