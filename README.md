You need openai key, huggingface key to access models and redis key if you have more data that you want to scrape
# README: Sentiment Analysis and Personalized Messaging for Clinical Trial Recruitment

##  Project Overview**

This project demonstrates the application of ethical web scraping, sentiment analysis, and AI-powered personalized messaging to identify potential participants for clinical trials. By analyzing posts and comments from Reddit, the project gauges user sentiments and interest levels toward clinical trials. Using these insights, the project generates customized outreach messages to engage users, leveraging the OpenAI API for dynamic message creation. The goal is to provide a scalable and ethical framework for clinical trial recruitment.

## Data source: 
The data is sourced from Reddit using its API. The project specifically targets two subreddits:

    -  `r/clinicaltrials`: A subreddit for discussing clinical trials, including participation and experiences.
    - `r/clinicalresearch`: A subreddit focused on research and professional discussions related to clinical trials.

Reddit's API provides access to posts and comments in these communities for analysis.

## Project Requirement 
To run this project, you'll need API keys for Reddit, Hugging Face, and OpenAI. These keys must be stored in a .env file in the following format:
```plaintext
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_user_agent
HUGGINGFACE_API_KEY=your_huggingface_api_key
OPENAI_API_KEY=your_openai_api_key
```
How to Obtain API Keys

## **How to Obtain API Keys**

- **Reddit API**:  
1. Visit [Reddit App Preferences](https://www.reddit.com/prefs/apps).
2. Click **"Create App"** or **"Create Another App"**.
3. Fill in the required fields:
    - **App Type**: Choose "script."
    - **Name**: Provide a descriptive name for your app.
    - **Redirect URI**: Use `http://localhost` (for testing purposes).
4. After creating the app, you'll see the **Client ID** (under the app name) and **Client Secret**.
5. Use a descriptive **User Agent** string (e.g., `myAppName:v1.0 (by /u/yourUsername)`).

For additional guidance, refer to this video tutorial:  
[YouTube: How to get Reddit API keys](https://www.youtube.com/watch?v=x9boO9x3TDA)

---

- **Hugging Face API**:  
1. Create a Hugging Face account or log in at [Hugging Face](https://huggingface.co/).
2. Navigate to your profile and select **"Access Tokens"**.
3. Click **"New Token"** to generate an API key.
4. Set the scope for your API key (e.g., read/write access) based on your project requirements.

For detailed steps, visit:  
[Hugging Face: API Tokens Documentation](https://huggingface.co/docs/hub/security-tokens)

---

- **OpenAI API**:  
1. Sign up or log in to [OpenAI](https://platform.openai.com/).
2. Go to **"API Keys"** under the **Personal Settings** menu.
3. Click **"Create new secret key"** to generate your API key.
4. Copy the key and store it securely. Note that you will not be able to view the full key again after navigating away.

For a step-by-step walkthrough, watch this video tutorial:  
[YouTube: OpenAI API Key Setup](https://www.youtube.com/watch?v=RwVHrUhY_DQ)

## Problems Addressed:

### 1. Identifying Relevant Discussions:
    
Filter Reddit posts and comments to focus on individuals expressing interest or experience in clinical trials, avoiding 
unrelated topics like news or career development.

### 2. Understanding Sentiment and Topics:
Analyze user sentiment and topic trends to uncover key themes and concerns in clinical trial discussions.

### 3. Determining User Interest:
Develop a scoring system to rank users' interest levels based on activity, sentiment, and intent.

### 4. Personalized User Engagement:
Generate tailored messages for users, emphasizing their suitability for clinical trials based on demographic and contextual information.

## Methodology

### 1. **Data Collection and Filtering**
- Scraped posts and comments from the subreddits `r/clinicalresearch` and `r/clinicaltrials` using a custom script (`reddit_scrapping.py`).
- Calculated a similarity score for posts based on cosine similarity between a predefined query and the post's title and body text.
- Penalized posts focused on career discussions and rewarded those discussing clinical trial experiences or participation to filter for relevant content.

### 2. **Sentiment and Topic Analysis**
- **Sentiment Analysis:**
  - Used the "cardiffnlp/twitter-roberta-base-sentiment-latest" pre-trained model to classify posts and comments into positive, neutral, or negative sentiments.
  - Combined longer posts' title and body text, split into chunks, and determined the dominant sentiment across chunks.
- **Topic Modeling:**
  - Applied LDA (Latent Dirichlet Allocation) to identify overarching themes across posts and comments.
  - Performed sentiment-specific topic modeling to uncover topics strongly associated with positive, neutral, and negative sentiments.
- **TF-IDF Analysis:**
  - Used TF-IDF to identify significant keywords and key phrases associated with each sentiment category.

### 3. **User Interest Scoring**
- Developed a weighted scoring system to rank users based on:
  1. **Activity:** Frequency of posts and comments normalized into an activity score (30% weight).
  2. **Sentiment:** Positive sentiment adds to the score, neutral sentiment contributes moderately, and negative sentiment detracts (20% weight).
  3. **Intent Detection:** Posts with phrases like "want to join" or "how to participate" are scored for strong intent (50% weight).
- Combined these metrics into a single interest score:
  $$\text{Interest Score} = w_1 \times \text{Activity Score} + w_2 \times \text{Sentiment Score} + w_3 \times \text{Intent Score}$$
  where $w_1 = 0.3$, $w_2 = 0.2$, and $w_3 = 0.5$.

### 4. **Personalized Messaging**
- Aggregated all posts and comments from high-interest users into a single text string.
- Used GPT with a custom prompt to extract demographic and contextual details, such as:
  - Gender, age, research topics, health conditions, location, etc.
- Generated tailored messages highlighting users' suitability for clinical trials,


## Address Data Privacy and User Engagement 
### Data Privacy: 
- All data was collected using Reddit's official API, ensuring compliance with their data usage policies.
- Reddit API won't allow user email address and user name extraction so the user are fairly anonymized 

### User Engagement: 
- Personalized messages are created only for users with medium-to-high-interest scores, ensuring relevance and minimizing spam or irrelevant outreach.
- The scoring system accounts for user activity and explicit intent to engage, focusing on those most likely to benefit from clinical trial participation.
- If users do not provide explicit information (e.g., gender, age, or location), default placeholders are used to ensure inclusive and non-intrusive messaging.
- The project analyzes solely publicly shared data without assumptions or inferences

## Challenges and Reflection: 
Some of the issue of the current solutions:
- Balancing the need for comprehensive Reddit data with ethical and practical constraints on scraping. Determining how to scrape more effectively without over-collecting data remains a challenge.
- Currently, all scraped data is stored in a single post_data.json file, which works for small datasets. However, as the dataset grows, there is a need to evaluate whether to transition to a relational database for structured data or a NoSQL solution for greater flexibility. 
- While the proposed solution for personalized messages is robust, it suffers from inefficiency due to repeated information when aggregating posts and their associated comments, leading to redundant contexts and occasional hallucinations in generated outputs.
- The current approach of penalizing or rewarding similarity scores based on specific keywords is cost-effective but static. I would like to explore a more dynamic and scalable method that is not relied on commercialized LLM solutions like GPT or Claude 

## Acknowledgement 
I acknowledge the assistance of ChatGPT and Claude  in debugging code and fine-tuning prompts for this projects