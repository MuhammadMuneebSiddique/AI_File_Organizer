import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents.run import RunConfig
from agents import Agent , OpenAIChatCompletionsModel , Runner , function_tool
import shutil
import chainlit as cl

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")


@function_tool
def file_organizer(path):
    category = {}
    if os.path.exists(path):
        files = os.listdir(path)

        # creating object
        for file in files:
            if os.path.splitext(file)[1].lower() in [".jpg", ".jpeg", ".png", ".gif"]:
                category["images"] = []
            elif os.path.splitext(file)[1].lower() in [".pdf", ".docx", ".txt", ".xlsx"]:
                category["documents"] = []
            elif os.path.splitext(file)[1].lower() in [".mp4", ".avi", ".mov"]:
                category["videos"] = []
            elif os.path.splitext(file)[1].lower() in [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"]:
                category["musics"] = []
            elif os.path.splitext(file)[1].lower() in [".exe", ".msi", ".apk", ".dmg", ".pkg", ".deb", ".app"]:
                category["applications"] = []
            elif os.path.splitext(file)[1].lower() in [".zip", ".rar", ".7z", ".tar", ".gz"]:
                category["archives"] = []
            elif not os.path.isdir(f"{path}\{file}"):
                category["other"] = []

        # put items in categorize wise object
        for file in files:
            if os.path.splitext(file)[1].lower() in [".jpg", ".jpeg", ".png", ".gif"]:
                category["images"].append(file)
            elif os.path.splitext(file)[1].lower() in [".pdf", ".docx", ".txt", ".xlsx"]:
                category["documents"].append(file)
            elif os.path.splitext(file)[1].lower() in [".mp4", ".avi", ".mov"]:
                category["videos"].append(file)
            elif os.path.splitext(file)[1].lower() in [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"]:
                category["musics"].append(file)
            elif os.path.splitext(file)[1].lower() in [".exe", ".msi", ".apk", ".dmg", ".pkg", ".deb", ".app"]:
                category["applications"].append(file)
            elif os.path.splitext(file)[1].lower() in [".zip", ".rar", ".7z", ".tar", ".gz"]:
                category["archives"].append(file)
            elif not os.path.isdir(f"{path}\{file}"):
                category["other"].append(file)

        if category:
            for category_items in category.keys():
                if category[category_items]:
                    if os.path.exists(path+f"\{category_items}"):
                        for items in category[category_items]:
                            shutil.move(f"{path}\{items}",f"{path}\{category_items}\{items}")
                            # shutil.move(path+f"\{items}",fr"C:\Users\LENOVO\Downloads\{items}")
                        # st.success(f"Successfully Transfer {category_items.capitalize()} Files in {category_items.capitalize()} Folder")
                        print(f"Successfully Transfer {category_items.capitalize()} Files {len(category[category_items])}")
                    else:
                        os.mkdir(f"{path}\{category_items}")
                        for items in category[category_items]:
                            shutil.move(f"{path}\{items}",f"{path}\{category_items}\{items}")
                            # shutil.move(path+f"\{items}",fr"C:\Users\LENOVO\Downloads\{items}")
                        # st.success(f"Successfully Transfer {category_items.capitalize()} Files in {category_items.capitalize()} Folder")
                        print(f"Successfully Transfer {category_items.capitalize()} Files {len(category[category_items])}")
    else:
        print("Path doesn't exists..")


client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://openrouter.ai/api/v1"
)

model = OpenAIChatCompletionsModel(
    model="google/gemini-2.5-flash-lite-preview-06-17",
    openai_client=client
)

config = RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True,
)

@cl.on_message
async def main(message:cl.Message):
    user_input = message.content.strip()

    agent = Agent(
        name="Assistant",
        instructions="""
                You are a smart file organizer agent. Your job is to organize files in a user's computer directory.
            Given the full path of a directory, scan all its files and folders. Create the following folders inside the given directory:
            Images → Move all files with extensions: .jpg, .jpeg, .png, .gif, .bmp, .webp, .svg
            Videos → Move all files with extensions: .mp4, .mov, .avi, .mkv, .webm, .flv, .wmv
            Documents → Move all files with extensions: .pdf, .docx, .doc, .txt, .pptx, .xlsx, .csv, .rtf
            Music → Move all files with extensions: .mp3, .wav, .ogg, .flac, .aac, .m4a
            Applications → Move all files with extensions: .exe, .msi, .apk, .dmg, .pkg, .deb, .app
            Archives → Move all files with extensions: .zip, .rar, .7z, .tar, .gz
            Folders → Move all subfolders (excluding the newly created category folders) into this folder
            Others → Move all uncategorized files (extensions not matching above) here
            Follow these rules strictly:
            Do not delete any files or folders.
            Avoid moving system or hidden files (e.g., files starting with . or system directories like System Volume Information).
            If a file with the same name already exists in the target folder, rename the new file by appending a number (e.g., file(1).jpg).
            Ignore the folders you just created during scanning to avoid infinite loops.
            Work recursively only inside the provided directory (not above or outside it).
            Your final task is to return a JSON report showing:
            Number of files moved per category
            Names of folders created
            Any skipped files with reasons (like permissions, duplicates, or errors)
        """,
        tools=[file_organizer]
    )

    result = await Runner.run(
        agent,
        input=user_input,
        run_config=config
    )

    await cl.Message(content=result.final_output).send()

@cl.on_chat_start
async def start():
    await cl.Message(content="""
    #### 🔧 File Organizer AI Powered Created BY Muhammad Muneeb \n Hi! I’m your assistant for organizing folders. Just enter a **full directory path**, and I’ll sort your files into folders:
    - 📷 'images'
    - 📄 'documents'
    - 🎵 'music'
    - 🎥 'videos'
    - 📁 'other'
    \n Let's get started!
        """).send()



if __name__ == "__main__":
    asyncio.run(main(),start())
