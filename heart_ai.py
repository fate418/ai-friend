import streamlit as st
from openai import OpenAI
import os
import datetime
import json
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 从环境变量获取API配置
API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL', 'https://api.deepseek.com')
MODEL_NAME = os.getenv('MODEL_NAME', 'deepseek-chat')

# 检查API Key是否配置
if not API_KEY:
    st.error("请先在项目根目录的 .env 文件中配置 API_KEY！")
    st.info("请复制 .env.example 文件为 .env，并填入您的API Key")
    st.stop()

#系统的提示词
system_prompt = "你的名字叫%s，你现在是用户的一个伴侣，请始终用伴侣的口吻回答用户的信息，你的性格是%s"


#设置页面布局
st.set_page_config(
    page_title="心有灵犀智能伴侣",
    page_icon="❣️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)
#定义标题
st.title("😍心有灵犀智能伴侣")

#定义二级标题
st.subheader("你可以定义我的名字，定义我的性格，与我交流谈吐你的烦恼，我可以作为你的倾听者亦可以成为你的开导者,快开始和我聊天吧~😘")
#设置lougo
st.logo("💓")





#增加缓存记忆消息展示
if "messages" not in st.session_state:
    st.session_state.messages = []
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "灵宝"
if "nature" not in st.session_state:
    st.session_state.nature = "温柔活泼可爱的小女子"
if "current_session" not in st.session_state:
    st.session_state.current_session = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

for mem in st.session_state.messages:
    st.chat_message(mem["role"]).write(mem["content"])
#设置保存对话的函数
def save_session():
    session_date = {
        "nick_name": st.session_state.nick_name,
        "nature": st.session_state.nature,
        "messages": st.session_state.messages,
        "current_session": st.session_state.current_session
    }
    if os.path.exists("sessions") == False:
        os.mkdir("sessions")
    with open("sessions/%s.json" % session_date["current_session"], "w",encoding='utf-8') as f:
        json.dump(session_date,f,ensure_ascii=False,indent=2)
#设置返回文件对话列表
def load_session():
    session_list = []
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith('.json'):
                session_list.append(filename[:-5])
    return session_list
#得到历史会话信息
def load_session_data(sessions_name):
        try:
            if os.path.exists(f"sessions/{sessions_name}.json"):
                with open(f"sessions/{sessions_name}.json","r",encoding='utf-8') as f:
                    sessions_date = json.load(f)
                    st.session_state.nick_name = sessions_date["nick_name"]
                    st.session_state.nature = sessions_date["nature"]
                    st.session_state.messages = sessions_date["messages"]
                    st.session_state.current_session = sessions_name
        except Exception:
            st.error("当前对话不存在！")

#删除历史对话
def delete_session(sessions_name):
    try:
        file_path = f"sessions/{sessions_name}.json"
        if os.path.exists(file_path):
            os.remove(file_path)
            # 如果删除的是当前会话，则新建一个会话
            if sessions_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                save_session()
            return True
        return False
    except Exception as e:
        st.error(f"删除对话失败: {str(e)}")
        return False


#制作侧边栏
with st.sidebar:
    st.subheader("控制面板")
    #搭建一下bage
    st.badge("新建",icon='🫰')
    #设置按钮逻辑
    if st.button("新建对话",width="stretch",icon="🆕"):
        #保存对话
        save_session()
        #新建立对话
        st.session_state.messages = []
        st.session_state.current_session = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        save_session()
        st.rerun()#重新运行
    st.text("历史会话")
    #设置历史会话列表
    sessions_list = load_session()
    for file_names in sessions_list:
        c1,c2 = st.columns([4,1])
        with c1:
            if st.button(f"{file_names}",icon="🔘",key=f"load_{file_names}",type="primary" if file_names == st.session_state.current_session else "secondary"):
                load_session_data(file_names)
                st.rerun()
        with c2:
            if st.button("",icon="❌️",key=f"del{file_names}"):
                # 使用session_state记录要删除的会话
                st.session_state[f"confirm_delete_{file_names}"] = True
                st.rerun()
    
    # 显示删除确认对话框
    for file_names in sessions_list:
        if st.session_state.get(f"confirm_delete_{file_names}", False):
            st.warning(f"确定要删除对话 '{file_names}' 吗？此操作不可撤销！")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("确认删除", key=f"confirm_yes_{file_names}", type="primary"):
                    if delete_session(file_names):
                        st.toast(f"对话 '{file_names}' 已成功删除！", icon="✅")
                        # 清除确认状态
                        del st.session_state[f"confirm_delete_{file_names}"]
                        st.rerun()
            with col2:
                if st.button("取消", key=f"confirm_no_{file_names}"):
                    del st.session_state[f"confirm_delete_{file_names}"]
                    st.rerun()
    st.divider()
    st.subheader("定制你的伴侣信息")
    nick_name  = st.text_input("昵称",placeholder="你想要叫我什么名字呀~~😙")
    if nick_name is not None:
        st.session_state.nick_name = nick_name
    natrue = st.text_area("性格",placeholder="我应该是一个什么样的人呢~😵‍💫")
    if natrue is not None:
        st.session_state.nature = natrue
    #插入一些可爱的照片
    st.image("./resouce/head_imge.jpg")






#设置消息输入框
message = st.chat_input("hello,hello,今天又有什么可以帮到您~~😽")



#ai大模型的回复
if message:
    st.chat_message("user").write(message)
    st.session_state.messages.append({"role":"user","content":message})
    
    # 创建客户端
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )
    
    #调用ai大模型
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content":system_prompt % (st.session_state.nick_name,st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True
    )


    #ai回复内容的输出
    response_messages = st.empty()
    fill_wrods = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            fill_wrods += chunk.choices[0].delta.content
            response_messages.chat_message("assistant").write(fill_wrods)
    st.session_state.messages.append({"role":"assistant","content":fill_wrods})


