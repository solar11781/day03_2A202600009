from datetime import datetime
from src.core.llm_provider import LLMProvider

def calculate_date_with_llm(args_str: str, llm: LLMProvider) -> str:
    """
    Tool tính ngày tháng sử dụng LLMProvider để đọc hiểu ngôn ngữ tự nhiên.
    Luôn trả về chuỗi chứa một số nguyên. Trả về "-1" nếu lỗi.
    """
    args_str = args_str.strip("'\" ")
    if not args_str:
        return "-1"
        
    # 1. Lấy mốc thời gian thực tế của hệ thống
    now = datetime.now()
    today_str = now.strftime('%d/%m/%Y')
    
    # 2. Xây dựng System Prompt & User Prompt bằng tiếng Anh
    system_prompt = """
    You are a time analysis tool. 
    Your task is to read the request and determine how many days the user wants you to schedule for their study plan.
    Return the number of days as an integer.
    If the user's request is a general question without a specific timeframe, return a suggested reasonable number of days based on the context. 
    If the duration cannot be determined at all, return -1.
    ABSOLUTELY NO explanations, NO punctuation marks. If you cannot calculate it, return -1.
    """
    
    user_prompt = f"Today is {today_str}. User request: '{args_str}'"
    
    try:
        # 3. Gọi LLM thông qua provider được truyền vào
        result_dict = llm.generate(prompt=user_prompt, system_prompt=system_prompt)
        
        # 4. Trích xuất text từ dictionary trả về
        llm_response = result_dict["content"].strip()
        
        # 5. Parse kết quả
        so_ngay = int(llm_response)
            
        return str(so_ngay)
        
    except ValueError:
        return "-1"
    except Exception as e:
        return "-1"