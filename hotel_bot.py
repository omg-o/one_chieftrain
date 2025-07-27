import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.retrievers import WikipediaRetriever
from langchain.memory import ConversationBufferWindowMemory
from .database import DatabaseManager

class HotelConciergeBot:
    def __init__(self, gemini_api_key: str, google_cloud_api_key: str, 
                 pdf_path: str, hotel_info: Dict[str, Any]):
        """
        Initialize the Hotel Concierge Bot for a specific hotel
        """
        self.gemini_api_key = gemini_api_key
        self.google_cloud_api_key = google_cloud_api_key
        self.pdf_path = pdf_path
        self.hotel_info = hotel_info
        
        # Initialize conversation history
        self.conversation_history = []
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Initialize LangChain components
        self.init_langchain_components()
        
        # Initialize vector store
        self.vector_store = None
        self.pdf_retriever = None
        
        # Load hotel-specific PDF document
        self.load_pdf_document()
    
    def init_langchain_components(self):
        """Initialize LangChain components"""
        # Initialize Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.gemini_api_key,
            temperature=0.7
        )
        
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=self.google_cloud_api_key
        )
        
        # Initialize Wikipedia retriever
        self.wikipedia_retriever = WikipediaRetriever(
            top_k_results=2,
            doc_content_chars_max=2000
        )
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=10,
            memory_key="chat_history",
            return_messages=True
        )
    
    def load_pdf_document(self):
        """Load and process the hotel-specific PDF document"""
        try:
            if not os.path.exists(self.pdf_path):
                print(f"Warning: PDF file not found at {self.pdf_path}")
                return
            
            # Load PDF document
            loader = PyPDFLoader(self.pdf_path)
            documents = loader.load()
            
            if not documents:
                print("No content found in PDF")
                return
            
            # Text splitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=[". ", "! ", "? ", "\n\n", "\n", " "]
            )
            
            # Split documents
            splits = text_splitter.split_documents(documents)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
            self.pdf_retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 2}
            )
            
            print(f"✅ Loaded {len(splits)} document chunks from {self.hotel_info['name']} PDF")
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
    
    def create_dynamic_prompt(self, human_question: str) -> str:
        """Create dynamic prompt with hotel context and conversation history"""
        # Get recent conversation history
        recent_history = self.conversation_history[-20:]
        history_text = ""
        
        for msg in recent_history:
            if msg['role'] == 'human':
                history_text += f"Guest: {msg['content']}\n"
            elif msg['role'] == 'assistant':
                history_text += f"Concierge: {msg['content']}\n"
        
        # Hotel-specific role prompt
        hotel_name = self.hotel_info.get('name', 'Our Hotel')
        hotel_location = self.hotel_info.get('location', '')
        hotel_description = self.hotel_info.get('description', '')
        
        role_prompt = f"""
You are the Chief Concierge of {hotel_name}, located in {hotel_location}.
{hotel_description}

You are the epitome of hospitality excellence, with deep knowledge of:
- Your hotel's specific amenities, services, and policies
- Local attractions and recommendations in {hotel_location}
- Dining options both within the hotel and nearby
- Transportation and logistics
- Special requests and concierge services

Always reference your hotel by name when appropriate and provide personalized 
recommendations based on your location and hotel type. You speak with elegance, 
warmth, and professional authority.
"""
        
        # Combine into dynamic prompt
        dynamic_prompt = f"""
{role_prompt}

RECENT CONVERSATION HISTORY:
{history_text}

CURRENT GUEST QUESTION: {human_question}

Please respond as the Chief Concierge of {hotel_name}, taking into account 
the conversation history and your hotel's specific context. Provide helpful, 
detailed, and personalized assistance.
"""
        
        return dynamic_prompt
    
    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """Search hotel-specific PDF documents"""
        if not self.pdf_retriever:
            return []
        
        try:
            docs = self.pdf_retriever.get_relevant_documents(query)
            return [{"content": doc.page_content, "source": doc.metadata} for doc in docs]
        except Exception as e:
            print(f"Document search error: {e}")
            return []
    
    def search_wikipedia(self, query: str) -> List[Dict[str, Any]]:
        """Search Wikipedia for general information"""
        try:
            # Include hotel location in search for better results
            location_query = f"{query} {self.hotel_info.get('location', '')}"
            docs = self.wikipedia_retriever.get_relevant_documents(location_query)
            return [{"content": doc.page_content[:1000], "source": "Wikipedia"} for doc in docs]
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return []
    
    def detect_booking_or_task(self, text: str) -> Dict[str, Any]:
        """Detect if the message contains booking request or task assignment"""
        booking_keywords = ['book', 'reserve', 'schedule', 'arrange', 'order']
        task_keywords = ['task', 'assign', 'please do', 'can you', 'need you to']
        
        text_lower = text.lower()
        
        result = {
            'is_booking': any(keyword in text_lower for keyword in booking_keywords),
            'is_task': any(keyword in text_lower for keyword in task_keywords),
            'detected_service': None,
            'details': text
        }
        
        # Extract service type for bookings
        services = ['restaurant', 'spa', 'room service', 'transport', 'tour', 'tickets']
        for service in services:
            if service in text_lower:
                result['detected_service'] = service
                break
        
        return result
    
    def process_message(self, human_message: str, guest_name: str = "Valued Guest") -> str:
        """Process human message and generate response"""
        # Add human message to history
        self.conversation_history.append({
            'role': 'human',
            'content': human_message,
            'timestamp': datetime.now()
        })
        
        # Create dynamic prompt
        dynamic_prompt = self.create_dynamic_prompt(human_message)
        
        # Detect booking or task
        booking_detection = self.detect_booking_or_task(human_message)
        
        # Search relevant information
        pdf_results = self.search_documents(human_message)
        wiki_results = []
        
        # If no relevant PDF content found, search Wikipedia
        if not pdf_results:
            wiki_results = self.search_wikipedia(human_message)
        
        # Prepare context
        context = ""
        if pdf_results:
            context += f"Relevant {self.hotel_info['name']} information:\n"
            for result in pdf_results:
                context += f"- {result['content']}\n"
        
        if wiki_results:
            context += f"\nGeneral information about {self.hotel_info.get('location', 'the area')}:\n"
            for result in wiki_results:
                context += f"- {result['content']}\n"
        
        # Create final prompt with context
        final_prompt = f"""
{dynamic_prompt}

RELEVANT INFORMATION:
{context}

Please provide a comprehensive response as the Chief Concierge of {self.hotel_info['name']}.
"""
        
        try:
            response = self.llm.predict(final_prompt)
            
            # Handle booking or task if detected
            if booking_detection['is_booking'] or booking_detection['is_task']:
                hotel_id = self.hotel_info['id']
                
                if booking_detection['is_booking']:
                    booking_data = {
                        'guest_name': guest_name,
                        'service_type': booking_detection.get('detected_service', 'general'),
                        'details': human_message
                    }
                    self.db.add_booking(hotel_id, booking_data)
                    response += f"\n\n✓ I have recorded your booking request and will ensure our team follows up promptly."
                
                if booking_detection['is_task']:
                    task_data = {
                        'description': human_message,
                        'assigned_to': 'Concierge Team',
                        'priority': 'medium'
                    }
                    self.db.add_task(hotel_id, task_data)
                    response += f"\n\n✓ I have noted your request and will ensure our team addresses it promptly."
            
            # Add AI response to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now()
            })
            
            return response
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an issue processing your request. Please try again or contact our front desk directly. Error: {str(e)}"
            return error_response
    
    def get_booking_history(self) -> List[Dict[str, Any]]:
        """Get booking history for this hotel"""
        hotel_id = self.hotel_info['id']
        return self.db.get_hotel_bookings(hotel_id)
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """Get task history for this hotel"""
        hotel_id = self.hotel_info['id']
        return self.db.get_hotel_tasks(hotel_id)