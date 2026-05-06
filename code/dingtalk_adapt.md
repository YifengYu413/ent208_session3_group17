1 ## 钉钉连接器媒体文件接收修复总结
2 
3 ### 核心问题
4 钉钉 Stream 模式下，收到的图片/文件/视频消息原先只返回占位符（如 `[图片]`），**没有实际下载媒体文件**。
5 
6 ### 改动文件
7 `/root/.openclaw/extensions/dingtalk-connector/plugin.ts`
8 
9 ---
10 
11 ### 改动 1：添加媒体下载函数（约 line 1155）
12 
13 ```typescript
14 // ============ 媒体下载 ============
15 
16 async function downloadDingTalkMedia(
17   downloadCode: string,
18   accessToken: string,
19   fileName: string,
20   config: any,  // 新增：需要 config 获取 clientId
21   log?: any,
22   maxSize: number = 20 * 1024 * 1024,
23 ): Promise<string | null> {
24   try {
25     const fs = await import('fs');
26     const path = await import('path');
27     const os = await import('os');
28 
29     const tempDir = path.join(os.tmpdir(), 'dingtalk-media');
30     if (!fs.existsSync(tempDir)) {
31       fs.mkdirSync(tempDir, { recursive: true });
32     }
33 
34     const filePath = path.join(tempDir, `${Date.now()}_${fileName}`);
35 
36     // 1. 使用新版 API 获取下载链接
37     const robotCode = config?.clientId;
38     if (!robotCode) {
39       log?.error?.(`[DingTalk][Media] 缺少 robotCode (clientId)`);
40       return null;
41     }
42 
43     const downloadUrlResp = await axios.post(
44       'https://api.dingtalk.com/v1.0/robot/messageFiles/download',
45       {
46         downloadCode: downloadCode,
47         robotCode: robotCode,
48       },
49       {
50         headers: {
51           'x-acs-dingtalk-access-token': accessToken,
52           'Content-Type': 'application/json',
53         },
54         timeout: 30_000,
55       }
56     );
57 
58     const downloadUrl = downloadUrlResp.data?.downloadUrl;
59     if (!downloadUrl) {
60       log?.error?.(`[DingTalk][Media] 获取下载链接失败`);
61       return null;
62     }
63 
64     // 2. 下载文件
65     const response = await axios.get(downloadUrl, {
66       responseType: 'arraybuffer',
67       timeout: 60_000,
68       maxContentLength: maxSize,
69     });
70 
71     // 检查文件大小
72     const fileSize = response.data?.length || 0;
73     if (fileSize > maxSize) {
74       log?.warn?.(`[DingTalk][Media] 文件过大: ${(fileSize/1024/1024).toFixed(1)}MB`);
75       return null;
76     }
77 
78     fs.writeFileSync(filePath, Buffer.from(response.data));
79     log?.info?.(`[DingTalk][Media] 下载成功: ${filePath}`);
80     return filePath;
81 
82   } catch (err: any) {
83     log?.error?.(`[DingTalk][Media] 下载失败: ${err.message}`);
84     return null;
85   }
86 }
87 ```
88 
89 ---
90 
91 ### 改动 2：修改 MessageContent 接口（约 line 1240）
92 
93 ```typescript
94 interface MessageContent {
95   text: string;
96   messageType: string;
97   mediaPath?: string;      // 单文件路径
98   mediaType?: string;      // image/video/audio/file
99   mediaPaths?: string[];   // 多文件路径（富文本多张图片）
100 }
101 ```
102 
103 ---
104 
105 ### 改动 3：修改 extractMessageContent 函数（约 line 1250）
106 
107 从同步函数改为异步函数，支持下载媒体：
108 
109 ```typescript
110 // 原函数签名
111 function extractMessageContent(data: any): { text: string; messageType: string }
112 
113 // 新函数签名
114 async function extractMessageContent(
115   data: any,
116   config: any,
117   log?: any,
118 ): Promise<MessageContent>
119 ```
120 
121 **各消息类型的处理逻辑：**
122 
123 ```typescript
124 switch (msgtype) {
125   case 'text':
126     return { text: data.text?.content?.trim() || '', messageType: 'text' };
127   
128   case 'picture': {
129     const downloadCode = data.content?.downloadCode || data.content?.mediaId;
130     if (downloadCode && config.enableMediaDownload !== false) {
131       const accessToken = await getAccessToken(config);
132       if (accessToken) {
133         const fileName = `image_${Date.now()}.jpg`;
134         const maxSize = config.mediaMaxSize || 20 * 1024 * 1024;
135         const filePath = await downloadDingTalkMedia(
136           downloadCode, accessToken, fileName, config, log, maxSize
137         );
138         if (filePath) {
139           return {
140             text: `[用户发送了图片: ${fileName}]`,
141             messageType: 'picture',
142             mediaPath: filePath,
143             mediaType: 'image',
144           };
145         }
146       }
147     }
148     return { text: '[图片]', messageType: 'picture' };
149   }
150   
151   case 'audio':
152   case 'video':
153   case 'file':
154     // 类似逻辑，使用 downloadCode 和 downloadDingTalkMedia
155   
156   case 'richText': {
157     // 提取富文本中的图片
158     const parts = data.content?.richText || [];
159     const textParts = parts.filter((p: any) => p.type === 'text')
160       .map((p: any) => p.text).join('');
161     const text = textParts || '[富文本消息]';
162     
163     const pictureParts = parts.filter((p: any) => p.type === 'picture');
164     if (pictureParts.length > 0 && config.enableMediaDownload !== false) {
165       const accessToken = await getAccessToken(config);
166       if (accessToken) {
167         const downloadedImages: string[] = [];
168         for (let i = 0; i < pictureParts.length; i++) {
169           const pic = pictureParts[i];
170           const downloadCode = pic.downloadCode || pic.mediaId;
171           const fileName = `richtext_image_${Date.now()}_${i}.jpg`;
172           const filePath = await downloadDingTalkMedia(
173             downloadCode, accessToken, fileName, config, log, maxSize
174           );
175           if (filePath) downloadedImages.push(filePath);
176         }
177         if (downloadedImages.length > 0) {
178           return {
179             text: `${text}\n\n[富文本中包含 ${downloadedImages.length} 张图片]`,
180             messageType: 'richText',
181             mediaPath: downloadedImages[0],
182             mediaType: 'image',
183             mediaPaths: downloadedImages,
184           };
185         }
186       }
187     }
188     return { text, messageType: 'richText' };
189   }
190 }
191 ```
192 
193 ---
194 
195 ### 改动 4：修改 handleDingTalkMessage 函数（约 line 2150）
196 
197 **调用 extractMessageContent 改为 await：**
198 ```typescript
199 const content = await extractMessageContent(data, dingtalkConfig, log);
200 if (!content.text && !content.mediaPath) return;
201 ```
202 
203 **添加媒体文件系统提示：**
204 ```typescript
205 if (content.mediaPaths && content.mediaPaths.length > 1) {
206   const mediaPrompt = `用户发送了 ${content.mediaPaths.length} 张图片，文件路径如下:\n${
207     content.mediaPaths.map((p, i) => `${i + 1}. ${p}`).join('\n')
208   }\n你可以直接引用这些路径来查看或处理图片。`;
209   systemPrompts.push(mediaPrompt);
210 } else if (content.mediaPath) {
211   const mediaPrompt = `用户发送了一个${
212     content.mediaType === 'image' ? '图片' : 
213     content.mediaType === 'video' ? '视频' : 
214     content.mediaType === 'audio' ? '语音' : '文件'
215   }，文件保存在: ${content.mediaPath}\n你可以直接引用这个路径来查看或处理该文件。`;
216   systemPrompts.push(mediaPrompt);
217 }
218 ```
219 
220 **构建 Gateway 用户内容时包含媒体引用：**
221 ```typescript
222 let userContent = content.text;
223 if (content.mediaPaths && content.mediaPaths.length > 1) {
224   // 多张图片（富文本）
225   const imageMarkdown = content.mediaPaths.map((p, i) => 
226     `![图片${i + 1}](${p})`
227   ).join('\n');
228   userContent = `${content.text}\n\n${imageMarkdown}`;
229 } else if (content.mediaPath) {
230   // 单张图片/文件
231   if (content.mediaType === 'image') {
232     userContent = `${content.text}\n\n![用户图片](${content.mediaPath})`;
233   } else {
234     userContent = `${content.text}\n\n[用户${
235       content.mediaType === 'video' ? '视频' : 
236       content.mediaType === 'audio' ? '语音' : '文件'
237     }: ${content.mediaPath}]`;
238   }
239 }
240 ```
241 
242 ---
243 
244 ### 改动 5：添加配置选项（约 line 2410）
245 
246 ```typescript
247 configSchema: {
248   schema: {
249     properties: {
250       // ... 原有配置 ...
251       enableMediaDownload: { 
252         type: 'boolean', 
253         default: true, 
254         description: 'Enable downloading media files (images, files, videos) from DingTalk' 
255       },
256       mediaMaxSize: { 
257         type: 'number', 
258         default: 20971520, 
259         description: 'Maximum media file size in bytes (default 20MB)' 
260       },
261     }
262   }
263 }
264 ```
265 
266 ---
267 
268 ### 关键要点
269 
270 | 项目 | 说明 |
271 |------|------|
272 | **下载 API** | `POST https://api.dingtalk.com/v1.0/robot/messageFiles/download` |
273 | **认证方式** | Header: `x-acs-dingtalk-access-token: {accessToken}` |
274 | **请求参数** | `downloadCode` + `robotCode`（即 clientId） |
275 | **获取方式** | 先调用 API 获取临时 `downloadUrl`，再下载文件 |
276 | **文件标识** | Stream 模式下使用 `downloadCode`，不是 `mediaId` |
277 | **Token 类型** | 下载用新版 `accessToken`（`getAccessToken`）<br>上传用旧版 `oapiToken`（`getOapiAccessToken`） |
278 
279 ---
280 
281 ### 复用步骤
282 
283 1. 备份原 `plugin.ts`
284 2. 添加 `downloadDingTalkMedia` 函数
285 3. 修改 `MessageContent` 接口
286 4. 修改 `extractMessageContent` 为异步，添加媒体下载逻辑
287 5. 修改 `handleDingTalkMessage`，处理媒体文件提示和内容构建
288 6. 添加 `enableMediaDownload` 和 `mediaMaxSize` 配置
289 7. 重启 Gateway