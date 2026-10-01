1.安装docker
brew install --cask docker
（这里要打开app 在 docker version）
2.配置代理（我这里没配置，因为国外image 开了本机代理也能拉，先不管）
3.docker run -d -p 8080:80 --name web nginx
（如果突然打不开docker desktop 就 
ps aux | grep -i docker | awk '{print $2}' | xargs kill -9 2>/dev/null 
）

4.nginx指定目录服务器部署
```bash
mkdir -p ~/docker-lab/site
echo "hello volume" > ~/docker-lab/site/index.html
docker run -d -p 8080:80 --name web -v ~/docker-lab/site:/usr/share/nginx/html:ro nginx
curl http://localhost:8080
echo "changed" > ~/docker-lab/site/index.html
curl http://localhost:8080
docker rm -f web
ls ~/docker-lab/site        # 容器删了，文件还在
```

5.命令解释
对应关系理解：
| 命令 | 作用 |
|---|---|
| `docker run` | 由 image 创建并启动一个 container |
| `docker ps` | 看正在运行的容器（`-a` 看全部，含已停止） |
| `docker logs` | 看容器内进程输出 |
| `docker stop` | 停止容器（不删除） |
| `docker rm` | 删除容器（不删除 image） |



## 验收对齐（做完要能勾掉）

- [✅] `docker run / ps / logs / stop / rm` 5 条命令独立完成
- [✅] 口头解释：image 与 container 的区别
image只读镜像，container是通过镜像运行的容器，不同name的容器里面有隔离的临时文件（volume可以读同一个文件）
- [✅] 口头解释：volume 的作用（为什么容器删了数据还在）
不论是 Docker.raw管理的 卷 还是 本机管理的 mount 都可以 不同 container 共用，跟container删除与否无关
- [✅] 产出：一个可用的 Docker 环境 + 一个最小运行示例
nginx实例