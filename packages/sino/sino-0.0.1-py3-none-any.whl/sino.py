

# te = 'cmd=GetDataObjectVersion&service={"中文&英文"}&formKey=SD_SaleOrder&mode=1&isYES2=true'

# td = 'cmd=GetDataObjectVersion&service={"中文%26英文"}&formKey=SD_SaleOrder&mode=1&isYES2=true'
# def dela(value):
#     if value.isdigit():
#         return int(value)
#     if value == 'True':
#         return True
#     if value == 'False':
#         return False
#     if value == "None":
#         return 'null'
#     return value

# def form_to_json(form):
#     json_body = {}
#     for i in form.split('&'):
#         json_body[i.split('=',1)[0]] = dela(i.split('=',1)[1])
#     # print(json_body)
#     form_data = json.dumps(json_body,separators=(',',':'),sort_keys=True).replace('"null"','null')
#     return form_data

# # print(form_to_json(te))
# ts = td.replace('%26','#::#')
# a = urllib.parse.unquote(ts)
# vv = urllib.parse.quote(a,safe=string.printable)
# print(a)


# y = 's={"中文&英文"}&a'
# with open('2.json') as f:
#     cfws = json.load(f)
#     tags_result = {}
#     for cfw in cfws.get('ports'):
#         ip = cfw.get('fixed_ips')[0].get('ip_address')
#         tags = cfw.get('tags')
#         tags_result[ip] = dict(x.split('=') for x in tags)
#     print(tags_result)

# text= "\u5927\u5bb6\u597d\uff1a\r\n        \u62a4\u7f51\u81ea\u4eca\u65e5\u8d77\u5f00\u59cb\u4e86\uff0c\u4e3a\u671f15\u5929\u3002\u8bf7\u5404\u9879\u76ee\u7ecf\u7406\u4ee5\u53ca\u7cfb\u7edf\u7ba1\u7406\u5458\u5173\u6ce8\u5404\u81ea\u8d1f\u8d23\u7684\u4fe1\u606f\u7cfb\u7edf\uff0c\u4ee5\u53ca\u4e2a\u4eba\u7535\u8111\u3002\u5982\u53d1\u73b0\u5f02\u5e38\u653b\u51fb\u884c\u4e3a\uff0c\u8bf7\u586b\u5199\u9644\u4ef6\uff0c\u4e0a\u62a5\u7ed9\u6211\u3002\r\n\r\n\r\n\r\n\u6606\u4ed1\u6570\u667a\u79d1\u6280\u6709\u9650\u8d23\u4efb\u516c\u53f8. \r\n \r\nKunlun Digital Technology Co.,Ltd.\r\n\u90e8\u95e8(Dept.)\uff1a\u7f51\u7edc\u5b89\u5168\u7814\u53d1\u90e8\r\n\u624b\u673a(Mobile)\uff1a18611902986\r\n\u90ae\u7bb1(E-mail)\uff1achengming01@cnpc.com.cn\r\n\u90ae\u7f16\uff08PC\uff09\uff1a102206\r\n\u5730\u5740(Add)\uff1a\u5317\u4eac\u5e02\u660c\u5e73\u533a\u6c99\u6cb3\u9547\u4e2d\u56fd\u77f3\u6cb9\u79d1\u6280\u521b\u65b0\u57fa\u5730A12\u5730\u5757B2\u5ea7218\u5ba4\r\n \r\n\u53d1\u4ef6\u4eba\uff1a kld_soc@cnpc.com.cn\r\n\u53d1\u9001\u65f6\u95f4\uff1a 2022-07-22 15:35\r\n\u6536\u4ef6\u4eba\uff1a \u6570\u667a\u7ecf\u7406; \u7f51\u7edc\u5b89\u5168\u7ba1\u7406\u5458\u7fa4\r\n\u6284\u9001\uff1a \u6768\u5fb7\u5fd7; \u4e1a\u52a1\u603b\u7ecf\u7406\u6210\u5458\u7fa4; quzhiyu@cnpc.com.cn; xuliang09\r\n\u4e3b\u9898\uff1a \u5173\u4e8e\u5f00\u5c552022\u5e74HW\u7684\u5de5\u4f5c\u901a\u77e5\r\n\u5404\u4f4d\u9886\u5bfc\u3001\u540c\u4e8b\uff0c\u60a8\u597d\uff1a\r\n    \u63a5\u96c6\u56e2\u516c\u53f8\u901a\u77e5\uff0c\u201c2022HW\u201d\u4e8e7\u670825\u65e5\u6b63\u5f0f\u5f00\u59cb\uff0c\u653b\u9632\u5408\u8ba1\u65f6\u957f\u4e3a15\u5929\uff0c\u653b\u9632\u65f6\u95f4\u6bb5\u4e3a9\u65f6\u81f321\u65f6\uff0c\u8282\u5047\u65e5\u4e0d\u4f11\u606f\uff0c\u8bf7\u5404\u7248\u5757\u3001\u533a\u57df\u7ec4\u7ec7\u3001\u5927\u533a\u79ef\u6781\u914d\u5408\u505a\u597d\u9632\u62a4\u5de5\u4f5c\uff0c\u5e76\u7ec4\u7ec7\u843d\u5b9e\u5b8c\u6210\u4ee5\u4e0b\u5de5\u4f5c\uff1a\r\n        1.\u5404\u4e1a\u52a1\u603b\u7ecf\u7406\u3001\u90e8\u95e8\u7ecf\u7406\u3001\u7f51\u7edc\u5b89\u5168\u7ba1\u7406\u5458\u53ca\u65f6\u5173\u6ce8\u5373\u65f6\u901a\u4fe1\u6606\u4ed1\u6570\u667a\u7f51\u5b89\u7fa4\u53ca\u201ckld_soc@cnpc.com.cn\u201d\u53d1\u5e03\u7684\u901a\u77e5\u3002\r\n        2.\u5404\u677f\u5757\u3001\u533a\u57df\u7ec4\u7ec7\u3001\u5927\u533a\u53ca\u7edf\u5efa\u7cfb\u7edf\u8d1f\u8d23\u4eba\u5b89\u6392\u4e13\u4eba7\u00d724\u5c0f\u65f6\uff08\u4fdd\u6301\u901a\u8baf\u7545\u901a\uff09\u5bf9\u8d23\u4efb\u8303\u56f4\u5185\u7684\u4fe1\u606f\u7cfb\u7edf\u3001\u7f51\u7edc\u8bbe\u5907\u3001\u5b89\u5168\u8bbe\u5907\u7b49\u8fdb\u884c\u76d1\u63a7\u3002\r\n        3.\u4e13\u4eba\u5bf9\u6240\u8f96\u4fe1\u606f\u8d44\u4ea7\u5305\u62ec\u4f46\u4e0d\u9650\u4e8e\u8fd0\u884c\u72b6\u6001\u3001\u544a\u8b66\u4fe1\u606f\u3001\u8fd0\u884c\u65e5\u5fd7\u548c\u5e10\u6237\u7b49\u5185\u5bb9\u8fdb\u884c\u76d1\u63a7\u548c\u5ba1\u8ba1\uff0c\u53d1\u73b0\u5f02\u5e38\uff0c\u7acb\u5373\u8fdb\u884c\u5206\u6790\u548c\u5904\u7406\u3002\r\n        4.\u4e00\u65e6\u53d1\u73b0\u7f51\u7edc\u653b\u51fb\u884c\u4e3a\uff0c\u505a\u597d\u5e94\u6025\u54cd\u5e94\u5904\u7f6e\uff0c\u5982\u679c\u6709\u80fd\u529b\u8ffd\u8e2a\u6eaf\u6e90\uff0c\u53ef\u8fdb\u884c\u76f8\u5e94\u7684\u5168\u94fe\u6761\u53d6\u8bc1\u548c\u53cd\u5236\u3002\u5426\u5219\uff0c\u5e94\u7acb\u5373\u963b\u65ad\u653b\u51fb\u884c\u4e3a\uff0c\u5e76\u622a\u53d6\u8bc1\u636e\u62a5\u516c\u53f8\u201c\u7f51\u7edc\u5b89\u5168\u4fdd\u969c\u5de5\u4f5c\u201d\u534f\u8c03\u7ec4\u3002\r\n        5.\u5404\u7f51\u7edc\u5b89\u5168\u7ba1\u7406\u5458\u5728\u6bcf\u65e5\u89c4\u5b9a\u65f6\u95f4\u5185\u901a\u8fc7\u6570\u5b57\u5316\u5de5\u4f5c\u53f0\u7684\u5f85\u529e\u4e0a\u62a5\u5f53\u65e5\u5b89\u5168\u72b6\u6001\u3002\r\n        6.\u516c\u53f8\u201c\u7f51\u7edc\u5b89\u5168\u4fdd\u969c\u5de5\u4f5c\u201d\u534f\u8c03\u7ec4\u6bcf\u65e5\u5411\u96c6\u56e2\u516c\u53f8\u4e0a\u62a5\u5f53\u65e5\u5b89\u5168\u72b6\u6001\u3002\r\n        7.\u7edf\u5efa\u4fe1\u606f\u7cfb\u7edf\u6309\u7167\u96c6\u56e2\u516c\u53f8\u8981\u6c42\u6bcf\u65e5\u6309\u65f6\u62a5\u9001\u5de5\u4f5c\u60c5\u51b5\u81f3\u7f51\u7edc\u5b89\u5168\u8fd0\u884c\u4e2d\u5fc3\u3002\r\n        8.\u5173\u4e8e\u7f51\u7edc\u5b89\u5168\u4e0a\u62a5\uff1a\r\n            \u53d1\u73b0\u7f51\u7edc\u5b89\u5168\u4e8b\u4ef6\u6216\u653b\u51fb\u884c\u4e3a\uff0c\u7531\u5404\u5355\u4f4d\u548c\u7edf\u5efa\u9879\u76ee\u7ec4\u7f51\u7edc\u5b89\u5168\u4f53\u7cfb\u76f8\u5173\u4eba\u5458\u586b\u62a5\u300a\u7f51\u7edc\u5b89\u5168\u4e8b\u4ef6\u4e0a\u62a5\u8868\u300b\u901a\u8fc7\u7535\u5b50\u90ae\u4ef6\u65b9\u5f0f\u5411\u4e0a\u62a5\u96c6\u56e2\u516c\u53f8\u7f51\u7edc\u5b89\u5168\u8fd0\u884c\u4e2d\u5fc3\uff0c\u7535\u5b50\u90ae\u4ef6\u4e3b\u9898\uff1a\u3010\u653b\u51fb\u4e0a\u62a5\u3011-\u5355\u4f4d\u540d\u79f0\uff0c\u653b\u51fb\u4e0a\u62a5\u4e13\u7528\u90ae\u7bb1\uff1asoc_sn@cnpc.com.cn\u3002\r\n            \u81ea\u5efa\u7cfb\u7edf\uff1a\r\n            \u8bf7\u7f51\u7edc\u5b89\u5168\u7ba1\u7406\u5458\u4e0a\u62a5\u81f3kld_soc@cnpc.com.cn\uff0c\u7531\u201d\u7f51\u7edc\u5b89\u5168\u4fdd\u969c\u5de5\u4f5c\u201c\u534f\u8c03\u7ec4\u7edf\u4e00\u4e0a\u62a5\u96c6\u56e2\u516c\u53f8\r\n            \u7edf\u5efa\u7cfb\u7edf\uff1a\r\n            \u8bf7\u6309\u96c6\u56e2\u516c\u53f8\u8981\u6c42\u4e0a\u62a5\u81f3soc_sn@cnpc.com.cn\uff0c\u540c\u65f6\u62a5\u5907\u201d\u7f51\u7edc\u5b89\u5168\u4fdd\u969c\u5de5\u4f5c\u201c\u534f\u8c03\u7ec4kld_soc@cnpc.com.cn\u3002\r\n\r\n    \u5982\u6709\u95ee\u9898\uff0c\u8bf7\u54a8\u8be2  \u66f2\u5fd7\u5b87 15631205605 \r\n    \u5982\u9700\u6280\u672f\u652f\u6301\uff0c\u8bf7\u54a8\u8be2\u5f90\u4eae 15810590892\r\n\r\n\r\n\r\n\u6606\u4ed1\u6570\u667a\u79d1\u6280\u6709\u9650\u8d23\u4efb\u516c\u53f8\r\n\u63d0\u9ad8\u7f51\u7edc\u5b89\u5168\u610f\u8bc6\uff0c\u8425\u9020\u5b89\u5168\u7f51\u7edc\u73af\u5883\u3002\r\n"

# se = text.split('\r\n')

# for s in se:
#     print(s)

# print('\u90ae\u4ef6\u5730\u533a\u516c\u53f8\u8d26\u53f7\u7ba1\u7406\u5458\u7ec4')

# POST /userx/?q=readmail&zid=5fb6f170b83949c26ae639d30c9e0386 HTTP/1.1
# Accept: */*
# Accept-Encoding: gzip, deflate, br
# Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
# Connection: keep-alive
# Content-Length: 102
# Content-type: application/x-www-form-urlencoded
# Cookie: emLoginUser=yuankexin%40cnpc.com.cn; DEVICE_ID=8721c600ea7ed4d65e154ca7d1125103f442373e; BIGipServerweb_80=696392458.20480.0000; EMPHPSID=9skh1k9m933e1fp193smaob771
# Host: mail.cnpc
# Origin: https://mail.cnpc
# Referer: https://mail.cnpc/userx/?q=base
# Sec-Fetch-Dest: empty
# Sec-Fetch-Mode: cors
# Sec-Fetch-Site: same-origin
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.33
# sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="102", "Microsoft Edge";v="102"
# sec-ch-ua-mobile: ?0
# sec-ch-ua-platform: "Windows"

# fid=1&sort=time.desc&page=1&iid=1251&filter=all&thread=0&conversation=0&is_report=0&is_search=0&words=




# zid=5fb6f170b83949c26ae639d30c9e0386


# s = 'EMPHPSID=2vr9o15bmu42kc1k3ofbaj3etd; path=/; HttpOnly, em_acct_name=deleted; expires=Thu, 01-Jan-1970 00:00:01 GMT; Max-Age=0; path=/client/, BIGipServerweb_80=377625354.20480.0000; path=/'

# s1 ='EMPHPSID=gpii18d7qe4g45afjombnah9sv; path=/; HttpOnly, DEVICE_ID=958dc0bbfba540dd0e6a4cfe2315bf1be2c13a4d; expires=Fri, 04-Aug-2023 04:12:54 GMT; Max-Age=31536000; path=/; HttpOnly, BIGipServerweb_80=612506378.20480.0000; path=/'

# print(s1.split(';')[0].split('=')[1])

# import time

# def is_between_time(begin_time,end_time):
#     now = time.strftime('%H:%M:%S')
#     if begin_time <= now <= end_time:
#         time.sleep(5)
#     else:
#         time.sleep(15)


# # begin_time = '07:00:00'
# # end_time = '16:00:00'

# with open('a.txt', 'r')as f:
#     headers = f.readlines()
#     re_headers = {}
#     for header in headers:
#         re_headers[header.split(':')[0]] = header.split(':')[1].strip()

# url = 'https://11.9.21.200:19290/ssoadapter/login?ticket=ST-32d2c316-cf3a-412c-a193-f1fc63dc093a&appId=62d670bd1d5a5414d35c1b2e&service=https%3A%2F%2F11.9.21.200%3A19290%2Fssoadapter%2Flogin%3Fservice%3Dhttps%3A%2F%2Fservice.manageone.cloud.cnpc%2Fmotenantconsolehomewebsite%2F'

# cookie = requests.get(url=url,headers=re_headers,verify=False,allow_redirects=False).headers

# # # print(cookie)

# # cookie = {
# #     'JSESSIONID':'2D376BD25AA724A6023322453B7435CA'
# # }

# url = 'https://11.9.21.200:19290/ssoadapter/login'


# resp = requests.get(url=url,cookies=cookie,headers=re_headers,verify=False,allow_redirects=False).headers
# print(resp)

# url1 = resp.get('Location')
# with open('b.txt', 'r')as f:
#     headers = f.readlines()
#     re_headers = {}
#     for header in headers:
#         re_headers[header.split(':')[0]] = header.split(':')[1].strip()

# # cookie = {
# #     'IAMIdentity':'X-184558539-0-11-z0ir4ynz49y01070vnf07eg8p1ndabnn9z2ved16sak6oucatkz'
# # }

# resp = requests.get(url=url1,cookies=cookie,headers=re_headers,verify=False,allow_redirects=False).headers

# print(resp)
# # sso_tgc = resp['SSOTGC']



# # SSOTGC=TGTX-0-185143413-217-EuH5bOVJZXqxpce4k4TCf2I5-sso
# sso_tgc = 'TGTX-0-185143413-225-qzsYHi4lYbZnUZx1PKXFtP0X-sso'
# url0 = 'https://auth.manageone.cloud.cnpc/authui/login?service=https%3A%2F%2Fservice.manageone.cloud.cnpc%2Fmotenantconsolehomewebsite%2F'
# cookie = {
#     'SSOTGC':sso_tgc,
#     # 'CID':'AgAAABJumqYzezVgbUYKG7E6OCU='
#     }

# with open('d.txt', 'r')as f:
#     headers = f.readlines()
#     resp_headers = {}
#     for header in headers:
#         resp_headers[header.split(':')[0]] = header.split(':')[1].strip()

# res = requests.get(url=url0,headers=resp_headers,cookies=cookie,verify=False,allow_redirects=False)
# print(res.headers.get('Location'))

# url = res.headers.get('Location')

# with open('c.txt', 'r')as f:
#     headers = f.readlines()
#     res_headers = {}
#     for header in headers:
#         res_headers[header.split(':')[0]] = header.split(':')[1].strip()

# resp = requests.get(url=url,headers=res_headers,verify=False,allow_redirects=False)
# print(resp.headers)
# import subprocess


# pid = 0
# p = subprocess.Popen('tasklist /FI "PID eq %s"' % pid)

# if p.stderr:
#     print(1)
# if p.poll():
#     print(2)
# text = p.communicate()

# print(text)

# 9128aca7-16ef-11ed-bbc7-fa163e93373
# 912c7d53-16ef-11ed-bbc7-fa163e93373

# 181f5846-16f1-11ed-bbc7-fa163e933730 申请者
# 182328f2-16f1-11ed-bbc7-fa163e933730 一级审批
# eb43511f-16f1-11ed-bbc7-fa163e933730 二级审批
# 2243836b-16f2-11ed-bbc7-fa163e933730 三级审批
# s1 = 0x16f1181f5846
# s2 = 0x16f1182328f2
# # print(s2-s1)
# print(0x16f1eb43511f - 0x16f1182328f2)
# print(0x16f22243836b - 0x16f1eb43511f)
# 40915122-16f4-11ed-bbc7-fa163e933730 申请者
# 409521ce-16f4-11ed-bbc7-fa163e933730 一级审批
# 8bfb590b-16f4-11ed-bbc7-fa163e933730 二级审批
# 19054e17-16f5-11ed-bbc7-fa163e933730 三级审批
# s3 = 0x16f440915122
# s4 = 0x16f4409521ce
# print(s4-s3)
# print(0x16f48bfb590b - 0x16f4409521ce)
# print(0x16f519054e17 - 0x16f48bfb590b)
# # d2dd60ba-16f7-11ed-bbc7-fa163e933730 申请者
# # d2e13166-16f7-11ed-bbc7-fa163e933730 一级审批
# # 363c1193-16f8-11ed-bbc7-fa163e933730 二级审批
# s5 = 0x16f7d2dd60ba
# s6 = 0x16f7d2e13166
# print(s6-s5)
# print(0x16f8363c1193 - 0x16f7d2e13166)
# print(0xfa163e933730bbc711ed16f8363c1193 - 0xfa163e933730bbc711ed16f8363c1193)

# import httpx

# # url = 'https://service.manageone.cloud.cnpc/vpc/rest/v1.5/35d2b1e398844b2ca1184c1844d1018a/publicIps?regionId=cn-jl-1&limit=0&marker='

# # header = {
# #     'Content-Type':'application/json;charset=utf8',
# #     'Authorization':'QLCL3wNKTmWmTXfaj5U6WvzO1d2zwmezKbyIauEx'
# # }

# # s = httpx.get(url,headers=header,verify=False)
# print('text')

# forwin = 'D:/forwin/Clash for Windows.exe'
# _p = subprocess.Popen(forwin)
# print(_p.pid)


# s = '5a388865-1f5c-11ed-9082-fa163eec3248'

# a = 0x5a388865

# b = a + 250028
# print()
# # 5a3c5911-1f5c-11ed-9082-fa163eec3248

# # 5a4b9b51-1f5c-11ed-9082-fa163eec3248

# # 35495aea-1f5e-11ed-9082-fa163eec3248

# # 35442aae-1f5e-11ed-9082-fa163eec3248

# s5 = 0x35442aae
# s6 = 0x35495aea

# s3 = 0x5a4b9b51
# s4 = 0x5a388865

# print(s6-s5)
# print(s3-s4)
# 以下代码报错：Exception ignored in: <function _ProactorBasePipeTransport.__del__ at 0x000002485B514F70> Traceback (most recent call last):


# def main():
#     # 其他流程
#     loop = asyncio.get_event_loop()
#     responses = loop.run_until_complete(test_asyncio())
#     for response in responses:
#         print(response)
#     loop.close()
#     # 其他流程

# if __name__ == '__main__':
#     main()

# import subprocess

# def main():
#     with open('greenbone.txt') as f:
#         data = f.readlines()
#         img_list = []
#         for images in data:
#             parts = images.split()
#             if parts[1] != 'latest':
#                 img_list.append(parts[0] + ":" + parts[1])
#             else:
#                 img_list.append(parts[2])
#     for img in img_list:
#         print(img)
#         # subprocess.call(["venv/Scripts/python.exe", "util/docker-pull.py", img])
#         # print(img)

# if __name__ == '__main__':
#     main()


# a = [1]
# a.append(2)
# a.append(3)
# print(a)

# print('a' in 'cli')
# -*- coding: utf-8 -*-
# import ipaddress

# ip_list = []

# with open('a.txt', 'r') as f:
#     for line in f:
#         ip = line.strip()
#         ip_list.append(ipaddress.IPv4Address(ip))

# networks = ipaddress.collapse_addresses(ip_list)

# with open('networks.txt', 'w') as f:
#     for network in networks:
#         f.write(str(network) + '\n')

import click

@click.group(invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
@click.option('-v', '--version', is_flag=True, help='Print version info and exit')
@click.option('--list', 'list_commands', is_flag=True, help='List installed commands')
@click.pass_context
def cli(ctx, version, list_commands):
    if ctx.invoked_subcommand is None:
        if version:
            click.echo('Version 1.0.0')
        elif list_commands:
            click.echo(cli.list_commands(ctx))
        else:
            click.echo(ctx.get_help())
@cli.command()
@click.option('-g', '--global', 'global_', is_flag=True, help='Use global package')
def install(global_):
    """Install a new binary"""
    if global_:
        click.echo('global test')
    else:
        click.echo('local test')

@cli.command()
def build():
    """Build a new package"""
    click.echo('Compiling the current package')

@cli.command()
@click.argument("package_name")
def new(package_name):
    """Create a new package"""
    click.echo(f"Creating package {package_name}...")

@cli.command()
def run():
    """Run a new package"""
    click.echo(f'Running of the local package')


if __name__ == '__main__':
    # cli()
    print(1/0)

