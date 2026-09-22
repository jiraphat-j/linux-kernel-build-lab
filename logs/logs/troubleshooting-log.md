cd linux-kernel-build-lab
git checkout -b troubleshooting
git pull origin main

git mv "logs/troubleshooting log/Screenshot 2026-09-19 191019.png" evidence/errors/ts01-vm-spec-insufficient.png
git mv "logs/troubleshooting log/Screenshot 2026-09-19 234329.png" evidence/errors/ts02-ubuntu-sources-unsaved.png
git mv "logs/troubleshooting log/Screenshot 2026-09-19 235837.png" evidence/errors/ts02-deb-src-error.png
git mv "logs/troubleshooting log/Screenshot 2026-09-19 235901.png" evidence/build/troubleshooter-deps-install-1.png
git mv "logs/troubleshooting log/Screenshot 2026-09-19 235914.png" evidence/build/troubleshooter-deps-install-2.png

# วางไฟล์ที่โหลดไปทับ logs/troubleshooting-log.md
git add .
git commit -m "docs(troubleshooting): rewrite log with root cause analysis TS-01..TS-06"
git push origin troubleshooting
