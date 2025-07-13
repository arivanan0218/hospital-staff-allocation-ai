# Hospital Staff Allocation AI

A comprehensive AI-powered hospital staff allocation system built with Python/FastAPI backend and React frontend, featuring intelligent scheduling using LangChain, LangGraph, and GROQ LLM.

## 🏥 Overview

This system automates hospital staff scheduling using advanced AI agents that consider:
- Staff skills, experience, and availability
- Shift requirements and priorities
- Department-specific needs
- Work-life balance and preferences
- Cost optimization
- Regulatory compliance

## 🚀 Features

### AI-Powered Allocation
- **Smart Agent System**: Multi-agent architecture with specialized roles
- **Constraint Validation**: Automated checking of work hour limits, skill requirements
- **Optimization Engine**: Multi-objective optimization (cost, quality, satisfaction)
- **Natural Language Processing**: GROQ LLM for intelligent decision making

### Staff Management
- Comprehensive staff profiles with skills, certifications, preferences
- Availability tracking and conflict detection
- Workload analysis and utilization metrics
- Skills gap identification

### Shift Scheduling
- Visual calendar interface with drag-and-drop functionality
- Real-time coverage analytics
- Priority-based shift allocation
- Flexible shift types (morning, afternoon, evening, night, on-call)

### Analytics & Reporting
- Real-time dashboard with key metrics
- Department and role-based analytics
- Cost analysis and optimization suggestions
- Allocation success rates and confidence scores

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.9+**: Core programming language
- **LangChain**: Framework for developing LLM applications
- **LangGraph**: For building complex multi-agent workflows
- **GROQ**: High-performance LLM inference
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server implementation

### Frontend
- **React 18**: Modern JavaScript library for building user interfaces
- **Vite**: Next generation frontend tooling
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Composable charting library built on React components
- **Lucide React**: Beautiful & consistent icon toolkit
- **React Hot Toast**: Smoking hot React notifications
- **Axios**: Promise-based HTTP client

### AI & ML
- **GROQ LLM**: For natural language processing and decision making
- **LangChain Agents**: For complex reasoning and tool usage
- **Multi-Agent System**: Specialized agents for allocation, constraints, and optimization

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.9+** (Download from [python.org](https://python.org))
- **Node.js 18+** (Download from [nodejs.org](https://nodejs.org))
- **npm** or **yarn** (comes with Node.js)
- **Git** (for cloning the repository)

## 🔧 Installation & Setup

### Step 1: Project Setup

1. **Create project directory**:
   ```bash
   mkdir hospital-staff-allocation-ai
   cd hospital-staff-allocation-ai
   ```

2. **Create the project structure**:
   ```bash
   # Create backend structure
   mkdir -p backend/app/{models,agents,services,data,utils,routers}
   
   # Create frontend structure
   mkdir frontend
   ```

### Step 2: Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Create requirements.txt** (copy the content from the requirements.txt artifact above)

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**:
   ```bash
   # Create .env file
   cp .env.example .env
   ```
   
   Edit `.env` file with your GROQ API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   APP_NAME=Hospital Staff Allocation AI
   DEBUG=True
   HOST=localhost
   PORT=8000
   ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
   ```

6. **Get GROQ API Key**:
   - Visit [GROQ Console](https://console.groq.com)
   - Sign up for a free account
   - Create an API key
   - Add it to your `.env` file

### Step 3: Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Initialize React project with Vite**:
   ```bash
   npm create vite@latest . -- --template react
   ```
   When prompted, choose "Yes" to proceed in the non-empty directory.

3. **Install dependencies**:
   ```bash
   npm install
   ```

4. **Install additional packages**:
   ```bash
   npm install axios react-router-dom lucide-react recharts date-fns react-hot-toast
   ```

5. **Install dev dependencies**:
   ```bash
   npm install -D tailwindcss postcss autoprefixer
   ```

6. **Initialize Tailwind CSS**:
   ```bash
   npx tailwindcss init -p
   ```

### Step 4: Add All Project Files

Copy all the code from the artifacts above into their respective files:

#### Backend Files
- Copy all Python files into their respective directories as shown in the project structure
- Ensure all `__init__.py` files are created
- Main entry point is `backend/app/main.py`

#### Frontend Files
- Copy React components into `frontend/src/components/`
- Copy services into `frontend/src/services/`
- Copy utilities into `frontend/src/utils/`
- Update configuration files (vite.config.js, tailwind.config.js, etc.)

### Step 5: Running the Application

#### Start the Backend Server

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Activate virtual environment** (if not already active):
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Start the FastAPI server**:
   ```bash
   python -m uvicorn app.main:app --reload --host localhost --port 8000
   ```

   The backend API will be available at:
   - **API**: http://localhost:8000
   - **Interactive Docs**: http://localhost:8000/docs
   - **Alternative Docs**: http://localhost:8000/redoc

#### Start the Frontend Development Server

1. **Navigate to frontend directory** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at:
   - **Application**: http://localhost:5173

### Step 6: Verify Installation

1. **Check Backend Health**:
   Visit http://localhost:8000/health - should show system status

2. **Check Frontend**:
   Visit http://localhost:5173 - should show the Hospital Staff Allocation AI dashboard

3. **Test API Integration**:
   The frontend should automatically connect to the backend and display data

## 📖 Usage Guide

### Getting Started

1. **Access the Dashboard**: Navigate to http://localhost:5173
2. **Explore Mock Data**: The system comes with pre-loaded demo data
3. **View Staff**: Go to Staff Management to see hospital staff members
4. **Check Shifts**: Use Shift Calendar to view and manage shifts
5. **AI Allocation**: Use the AI Allocation tab to automatically assign staff

### Key Operations

#### Adding Staff
1. Navigate to "Staff Management"
2. Click "Add Staff"
3. Fill in details (name, role, department, skills, etc.)
4. Set preferences for shift types
5. Save the staff member

#### Creating Shifts
1. Go to "Shift Calendar"
2. Click "Add Shift" 
3. Select date, time, department
4. Define required staff roles and quantities
5. Set priority level
6. Save the shift

#### AI Auto-Allocation
1. Open "AI Allocation" tab
2. Select date for allocation
3. Choose shifts to allocate
4. Configure AI settings (strategy, constraints)
5. Click "AI Auto-Allocate"
6. Review and approve suggested allocations

#### Optimization
1. Select date range
2. Choose optimization strategy (cost, quality, balance, satisfaction)
3. Click "Optimize Schedule"
4. Review optimization results and recommendations

## 🔧 Configuration

### AI Settings
- **Confidence Threshold**: Minimum confidence for auto-approval (0.5-1.0)
- **Optimization Strategy**: Cost, Quality, Balance, or Satisfaction focus
- **Constraints**: Work hour limits, skill requirements, preferences
- **Preferences**: Respect staff shift preferences, prefer experience

### System Settings
- **GROQ API Key**: Required for AI functionality
- **CORS Origins**: Allowed frontend URLs
- **Debug Mode**: Enable detailed logging
- **Database**: Currently uses in-memory storage (mock data)

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm run test
```

### Manual Testing
1. **Health Check**: http://localhost:8000/health
2. **API Documentation**: http://localhost:8000/docs
3. **Staff API**: http://localhost:8000/api/staff/
4. **Allocation Test**: Use the AI allocation feature with demo data

## 🔒 Security Considerations

- **API Keys**: Store GROQ API key securely in environment variables
- **CORS**: Configure allowed origins properly for production
- **Input Validation**: All inputs are validated using Pydantic models
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Consider implementing rate limiting for production

## 🚀 Deployment

### Production Setup

1. **Environment Variables**: Set production values
2. **Database**: Replace mock data with real database (PostgreSQL recommended)
3. **Authentication**: Implement user authentication and authorization
4. **HTTPS**: Use SSL/TLS certificates
5. **Process Management**: Use PM2, Supervisor, or Docker
6. **Reverse Proxy**: Use Nginx or Apache
7. **Monitoring**: Implement logging and monitoring

### Docker Deployment (Optional)

Create `Dockerfile` for backend:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=your_key_here
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **GROQ API Key Error**:
   - Verify API key is correct in `.env` file
   - Check GROQ console for usage limits

2. **Port Already in Use**:
   - Change ports in configuration files
   - Kill existing processes: `lsof -ti:8000 | xargs kill -9`

3. **Module Import Errors**:
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

4. **Frontend Build Errors**:
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Update Node.js to latest LTS version

5. **CORS Errors**:
   - Check ALLOWED_ORIGINS in backend `.env`
   - Ensure frontend URL matches allowed origins

### Getting Help

- **Issues**: Create an issue on GitHub
- **Documentation**: Check API docs at http://localhost:8000/docs
- **Logs**: Check backend logs for detailed error messages

## 🎯 Future Enhancements

- **Real Database Integration**: PostgreSQL/MySQL support
- **User Authentication**: Role-based access control
- **Mobile App**: React Native companion app
- **Advanced Analytics**: ML-powered insights
- **Integration APIs**: Connect with existing hospital systems
- **Notification System**: Email/SMS alerts for schedule changes
- **Audit Trail**: Complete change tracking
- **Multi-Hospital Support**: Support for hospital chains

## 📊 Performance

- **Backend**: FastAPI provides high-performance async API
- **Frontend**: React with Vite for fast development and building
- **AI Processing**: GROQ provides sub-second LLM responses
- **Scalability**: Designed for horizontal scaling

## 🌟 Acknowledgments

- **FastAPI Team**: For the excellent web framework
- **React Team**: For the robust frontend library
- **LangChain**: For the powerful LLM framework
- **GROQ**: For high-performance LLM inference
- **Tailwind CSS**: For the utility-first CSS framework

---

**Built with ❤️ for better healthcare workforce management**