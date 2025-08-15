// Global variables
let currentAnalysis = null;
let currentEgg = null;
let careQuestions = null;

// DOM Elements
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');
const createEggForm = document.getElementById('create-egg-form');
const analyzeImageForm = document.getElementById('analyze-image-form');
const loadingOverlay = document.getElementById('loading-overlay');
const loadingText = document.getElementById('loading-text');
const resultModal = document.getElementById('result-modal');
const modalContent = document.getElementById('modal-content');
const closeModal = document.querySelector('.close');
const analysisResult = document.getElementById('analysis-result');
const analysisContent = document.getElementById('analysis-content');
const createFromAnalysisBtn = document.getElementById('create-from-analysis');
const collectionContainer = document.getElementById('collection-container');
const toggleViewBtn = document.getElementById('toggle-view-btn');
const careModal = document.getElementById('care-modal');
const creatureModal = document.getElementById('creature-modal');
const revealModal = document.getElementById('reveal-modal');
const imageViewerModal = document.getElementById('image-viewer-modal');
const fullSizeImage = document.getElementById('full-size-image');
const careForm = document.getElementById('care-form');
const careQuestionsContainer = document.getElementById('care-questions');
const creatureContent = document.getElementById('creature-content');

// Tab Switching
tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const targetTab = button.getAttribute('data-tab');
        
        console.log('Tab switched to:', targetTab, 'currentEgg:', currentEgg);
        
        // Update active tab button
        tabButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        
        // Update active tab content
        tabContents.forEach(content => content.classList.remove('active'));
        document.getElementById(`${targetTab}-tab`).classList.add('active');
        
        // Load collection if collection tab
        if (targetTab === 'collection') {
            loadCollection();
        }
    });
});

// Create Egg Form
createEggForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const description = document.getElementById('description').value.trim();
    const descriptors = document.getElementById('descriptors').value
        .split(',')
        .map(d => d.trim())
        .filter(d => d.length > 0);
    
    if (!description || descriptors.length === 0) {
        showError('Please provide both a description and at least one descriptor.');
        return;
    }
    
    showLoading('Creating your magical egg...');
    
    try {
        const response = await fetch('/api/create-egg', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                description: description,
                descriptors: descriptors
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            hideLoading();
            showEggResult(result.egg);
            createEggForm.reset();
        } else {
            hideLoading();
            showError(result.message || 'Failed to create egg');
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
});

// Analyze Image Form (Streamlined Flow)
analyzeImageForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('image-upload');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select an image to analyze.');
        return;
    }
    
    showLoading('Analyzing your image and generating egg...');
    
    try {
        // Step 1: Analyze the image
        const formData = new FormData();
        formData.append('image', file);
        
        const analyzeResponse = await fetch('/api/analyze-image', {
            method: 'POST',
            body: formData
        });
        
        const analyzeResult = await analyzeResponse.json();
        
        if (!analyzeResult.success) {
            hideLoading();
            showError(analyzeResult.message || 'Failed to analyze image');
            return;
        }
        
        // Step 2: Automatically create egg from analysis
        const createResponse = await fetch('/api/create-egg', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                description: analyzeResult.analysis.description,
                descriptors: analyzeResult.analysis.descriptors
            })
        });
        
        const createResult = await createResponse.json();
        
        if (createResult.success) {
            hideLoading();
            currentEgg = createResult.egg;
            showEggResult(createResult.egg);
            // Show the analysis details as well
            showAnalysisResult(analyzeResult.analysis);
        } else {
            hideLoading();
            showError(createResult.message || 'Failed to create egg from analysis');
        }
    } catch (error) {
        hideLoading();
        showError('Network error: ' + error.message);
    }
});

// Global state for collection view
let isDetailedView = false;

// Load Collection (Eggs and Creatures)
async function loadCollection() {
    try {
        // Load both eggs and creatures
        const [eggsResponse, creaturesResponse] = await Promise.all([
            fetch('/api/eggs'),
            fetch('/api/creatures')
        ]);
        
        const eggsResult = await eggsResponse.json();
        const creaturesResult = await creaturesResponse.json();
        
        if (eggsResult.success && creaturesResult.success) {
            displayCollection(eggsResult.eggs, creaturesResult.creatures);
        } else {
            collectionContainer.innerHTML = '<div class="error">Failed to load collection</div>';
        }
    } catch (error) {
        collectionContainer.innerHTML = '<div class="error">Network error loading collection</div>';
    }
}

// Display Collection
function displayCollection(eggs, creatures) {
    // Create a map of eggs by ID for quick lookup
    const eggsMap = {};
    eggs.forEach(egg => {
        eggsMap[egg.id] = egg;
    });
    
    const allItems = [];
    
    // Add unhatched eggs to collection
    eggs.forEach(egg => {
        // Check if this egg has been hatched based on status
        if (egg.status !== 'hatched') {
            allItems.push({
                type: 'egg',
                data: egg,
                date: new Date(egg.created_at)
            });
        }
    });
    
    // Add creatures to collection (with their eggs)
    creatures.forEach(creature => {
        const originalEgg = eggsMap[creature.egg_id];
        allItems.push({
            type: 'creature',
            data: creature,
            egg: originalEgg,
            date: new Date(creature.hatched_at)
        });
    });
    
    // Sort by date (newest first)
    allItems.sort((a, b) => b.date - a.date);
    
    if (allItems.length === 0) {
        collectionContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-egg" style="font-size: 3rem; color: #4ecdc4; margin-bottom: 20px;"></i>
                <h3>No collection yet!</h3>
                <p>Create your first magical egg to get started.</p>
            </div>
        `;
        return;
    }
    
    collectionContainer.innerHTML = allItems.map(item => {
        if (item.type === 'egg') {
            return createEggCard(item.data);
        } else {
            return createCreatureCard(item.data, item.egg);
        }
    }).join('');
}

// Create Egg Card
function createEggCard(egg) {
    const descriptionClass = isDetailedView ? 'detailed' : 'compact';
    const shortDescription = egg.description.length > 100 ? 
        egg.description.substring(0, 100) + '...' : 
        egg.description;
    
    return `
        <div class="collection-card egg-card">
            <img src="${egg.image_url}" alt="Egg" class="collection-image" onclick="openImageViewer('${egg.image_url}')">
            <div class="collection-info">
                <div class="collection-title">
                    <i class="fas fa-egg"></i>
                    <span>Magical Egg</span>
                </div>
                <div class="collection-description ${descriptionClass}">
                    ${isDetailedView ? egg.description : shortDescription}
                </div>
                <div class="collection-descriptors">
                    ${egg.descriptors.map(desc => `<span class="descriptor-tag">${desc}</span>`).join('')}
                </div>
                <div class="collection-date">Created: ${new Date(egg.created_at).toLocaleDateString()}</div>
                <div class="egg-actions">
                    <button class="btn btn-primary btn-sm" onclick="hatchEggFromCollection('${egg.id}')">
                        <i class="fas fa-heart"></i> Hatch Now
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Create Creature Card
function createCreatureCard(creature, egg) {
    const descriptionClass = isDetailedView ? 'detailed' : 'compact';
    const shortDescription = creature.egg_description && creature.egg_description.length > 100 ? 
        creature.egg_description.substring(0, 100) + '...' : 
        (creature.egg_description || 'A unique creature hatched from a magical egg');
    
    return `
        <div class="collection-card creature-card" onclick="showCreatureDetail('${creature.id}')">
            <div class="creature-egg-comparison">
                <div class="egg-side">
                    <div class="egg-label">Original Egg</div>
                    <img src="${egg ? egg.image_url : ''}" alt="Original Egg" class="egg-thumbnail" onclick="event.stopPropagation(); openImageViewer('${egg ? egg.image_url : ''}')">
                </div>
                <div class="evolution-arrow">
                    <i class="fas fa-arrow-right"></i>
                </div>
                <div class="creature-side">
                    <div class="creature-label">Hatched Creature</div>
                    <img src="${creature.image_url}" alt="Creature" class="creature-thumbnail" onclick="event.stopPropagation(); openImageViewer('${creature.image_url}')">
                </div>
            </div>
            <div class="collection-info">
                <div class="collection-title">
                    <i class="fas fa-dragon"></i>
                    <span>${creature.name || 'Magical Creature'}</span>
                </div>
                <div class="collection-description ${descriptionClass}">
                    ${isDetailedView ? (creature.egg_description || 'A unique creature hatched from a magical egg') : shortDescription}
                </div>
                <div class="collection-descriptors">
                    ${creature.egg_traits ? creature.egg_traits.map(desc => `<span class="descriptor-tag">${desc}</span>`).join('') : ''}
                </div>
                <div class="collection-date">Hatched: ${new Date(creature.hatched_at).toLocaleDateString()}</div>
            </div>
        </div>
    `;
}

// Show Analysis Result
function showAnalysisResult(analysis) {
    analysisContent.innerHTML = `
        <div class="analysis-section">
            <h4>Egg Description:</h4>
            <p>${analysis.description}</p>
        </div>
        <div class="analysis-section">
            <h4>Egg Traits:</h4>
            <div class="descriptors-list">
                ${analysis.descriptors.map(desc => `<span class="descriptor-tag">${desc}</span>`).join('')}
            </div>
        </div>
    `;
    
    analysisResult.classList.remove('hidden');
}

// Show Egg Result
function showEggResult(egg) {
    console.log('Setting currentEgg to:', egg);
    currentEgg = egg;
    
    modalContent.innerHTML = `
        <h2 style="color: #4ecdc4; margin-bottom: 20px;">
            <i class="fas fa-egg"></i> Egg Created Successfully!
        </h2>
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="${egg.image_url}" alt="Created Egg" style="max-width: 100%; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
        </div>
        <div style="margin-bottom: 20px;">
            <h4>Description:</h4>
            <p>${egg.description}</p>
        </div>
        <div style="margin-bottom: 20px;">
            <h4>Descriptors:</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 5px;">
                ${egg.descriptors.map(desc => `<span class="descriptor-tag">${desc}</span>`).join('')}
        </div>
        </div>
        <div style="text-align: center;">
            <button class="btn btn-primary" onclick="startCareQuestionnaire()">
                <i class="fas fa-heart"></i> Care for My Egg
            </button>
            <button class="btn btn-secondary" onclick="closeResultModal()" style="margin-left: 10px;">
                <i class="fas fa-check"></i> Continue
            </button>
        </div>
    `;
    
    resultModal.classList.remove('hidden');
}

// Toggle View Button
toggleViewBtn.addEventListener('click', () => {
    isDetailedView = !isDetailedView;
    toggleViewBtn.innerHTML = isDetailedView ? 
        '<i class="fas fa-compress"></i> Compact View' : 
        '<i class="fas fa-expand"></i> Detailed View';
    
    // Reload collection with new view
    loadCollection();
});

// Show Egg Detail
function showEggDetail(eggId) {
    // This would fetch and show detailed egg information
    // For now, just show a placeholder
    modalContent.innerHTML = `
        <h2 style="color: #4ecdc4; margin-bottom: 20px;">
            <i class="fas fa-egg"></i> Egg Details
        </h2>
        <p>Detailed view for egg ${eggId} - Coming soon!</p>
        <div style="text-align: center; margin-top: 20px;">
            <button class="btn btn-primary" onclick="closeResultModal()">
                <i class="fas fa-times"></i> Close
            </button>
        </div>
    `;
    
    resultModal.classList.remove('hidden');
}

// Show Creature Detail
function showCreatureDetail(creatureId) {
    // This would fetch and show detailed creature information
    // For now, just show a placeholder
    modalContent.innerHTML = `
        <h2 style="color: #ff6b6b; margin-bottom: 20px;">
            <i class="fas fa-dragon"></i> Creature Details
        </h2>
        <p>Detailed view for creature ${creatureId} - Coming soon!</p>
        <div style="text-align: center; margin-top: 20px;">
            <button class="btn btn-primary" onclick="closeResultModal()">
                <i class="fas fa-times"></i> Close
            </button>
        </div>
    `;
    
    resultModal.classList.remove('hidden');
}

// Hatch Egg from Collection
async function hatchEggFromCollection(eggId) {
    try {
        // Get egg data
        const response = await fetch('/api/eggs');
        const result = await response.json();
        
        if (result.success) {
            const egg = result.eggs.find(e => e.id === eggId);
            if (egg) {
                currentEgg = egg;
                await startCareQuestionnaire();
            } else {
                showError('Egg not found');
            }
        } else {
            showError('Failed to load egg data');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    }
}

// Open Image Viewer
function openImageViewer(imageUrl) {
    if (!imageUrl) return;
    
    fullSizeImage.src = imageUrl;
    imageViewerModal.classList.remove('hidden');
}

// Close Image Viewer
function closeImageViewer() {
    imageViewerModal.classList.add('hidden');
}

// Utility Functions
function showLoading(message) {
    loadingText.textContent = message;
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function showError(message) {
    modalContent.innerHTML = `
        <h2 style="color: #ff6b6b; margin-bottom: 20px;">
            <i class="fas fa-exclamation-triangle"></i> Error
        </h2>
        <p>${message}</p>
        <div style="text-align: center; margin-top: 20px;">
            <button class="btn btn-primary" onclick="closeResultModal()">
                <i class="fas fa-times"></i> Close
            </button>
        </div>
    `;
    
    resultModal.classList.remove('hidden');
}

function closeResultModal() {
    resultModal.classList.add('hidden');
}

// Care Questionnaire Functions
async function startCareQuestionnaire() {
    try {
        console.log('Starting care questionnaire, currentEgg:', currentEgg);
        
        // Get care questions
        const response = await fetch('/api/care-questions');
        const result = await response.json();
        
        if (result.success) {
            careQuestions = result.questions;
            showCareQuestionnaire();
        } else {
            showError('Failed to load care questions');
        }
    } catch (error) {
        showError('Network error loading care questions');
    }
}

function showCareQuestionnaire() {
    console.log('Showing care questionnaire, currentEgg:', currentEgg);
    
    // Close egg result modal
    resultModal.classList.add('hidden');
    
    // Build questions HTML
    const questionsHTML = careQuestions.questions.map(q => `
        <div class="form-group">
            <label for="${q.id}">${q.question}</label>
            <textarea 
                id="${q.id}" 
                name="${q.id}" 
                placeholder="${q.placeholder}"
                required
            ></textarea>
        </div>
    `).join('');
    
    careQuestionsContainer.innerHTML = questionsHTML;
    careModal.classList.remove('hidden');
}

// Care Form Submission
careForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    console.log('Care form submitted, currentEgg:', currentEgg);
    
    if (!currentEgg) {
        showError('No egg found. Please create an egg first.');
        return;
    }
    
    // Collect care response (single question)
    const careResponses = {};
    const question = careQuestions.questions[0];
    const value = document.getElementById(question.id).value.trim();
    if (!value) {
        showError(`Please answer: ${question.question}`);
        return;
    }
    careResponses[question.id] = value;
    
    console.log('Care responses collected:', careResponses);
    
    // Close care modal and show loading
    careModal.classList.add('hidden');
    showLoading('✨ Hatching your unique creature...');
    
    // Update loading message during the process
    setTimeout(() => {
        if (loadingOverlay.classList.contains('hidden')) return;
        showLoading('🎨 Creating your magical creature...');
    }, 3000);
    
    setTimeout(() => {
        if (loadingOverlay.classList.contains('hidden')) return;
        showLoading('🎵 Giving your creature a voice...');
    }, 6000);
    
    try {
        console.log('Attempting to hatch creature with:', {
            egg_id: currentEgg.id,
            care_responses: careResponses
        });
        
        const response = await fetch('/api/hatch-creature', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                egg_id: currentEgg.id,
                care_responses: careResponses
            })
        });
        
        console.log('Response status:', response.status);
        const result = await response.json();
        console.log('Response result:', result);
        
        if (result.success) {
            hideLoading();
            startRevealCeremony(result.creature);
        } else {
            hideLoading();
            showError(result.message || 'Failed to hatch creature');
        }
    } catch (error) {
        console.error('Error during hatching:', error);
        hideLoading();
        showError('Network error: ' + error.message);
    }
});

// Reveal Ceremony Functions
let currentCreature = null;

function startRevealCeremony(creature) {
    currentCreature = creature;
    revealModal.classList.remove('hidden');
    
    // Start directly with silhouette stage
    showSilhouetteStage();
}

function showSilhouetteStage() {
    // Show silhouette stage directly
    document.getElementById('silhouette-stage').classList.remove('hidden');
    
    // Show creature reveal after silhouette
    setTimeout(() => {
        showCreatureReveal();
    }, 2000); // Show creature after 2 seconds
}

function showCreatureReveal() {
    // Hide silhouette stage, show creature reveal stage
    document.getElementById('silhouette-stage').classList.add('hidden');
    document.getElementById('creature-reveal-stage').classList.remove('hidden');
    
    // Set up creature image
    const creatureImage = document.getElementById('creature-reveal-image');
    creatureImage.src = currentCreature.image_url;
    
    // Set up creature name
    const creatureNameElement = document.getElementById('creature-reveal-name');
    creatureNameElement.textContent = currentCreature.name || 'Your Magical Creature';
    
    // Set up creature info
    document.getElementById('reveal-sound-text').textContent = `"${currentCreature.sound_text}"`;
    document.getElementById('reveal-voice-desc').textContent = currentCreature.voice_description;
    
    // Set up care details
    const careDetails = document.getElementById('reveal-care-details');
    const careQuestionId = Object.keys(currentCreature.care_responses)[0];
    const careResponse = Object.values(currentCreature.care_responses)[0];
    
    // Get the question text based on the ID
    const questionText = getQuestionText(careQuestionId);
    
    careDetails.innerHTML = `
        <p><strong>${questionText}</strong> ${careResponse}</p>
    `;
    
    // Set up play sound button
    const playSoundBtn = document.getElementById('play-sound-btn');
    if (currentCreature.audio_url) {
        playSoundBtn.onclick = () => playCreatureSound(currentCreature.audio_url);
    } else {
        playSoundBtn.style.display = 'none';
    }
    
    // Start the reveal animation
    setTimeout(() => {
        creatureImage.classList.add('revealed');
        
        // Play sound when creature appears
        if (currentCreature.audio_url) {
            playCreatureSound(currentCreature.audio_url);
        }
        
        // Show info after creature appears
        setTimeout(() => {
            document.getElementById('creature-reveal-info').classList.add('revealed');
        }, 1500);
    }, 500);
}

function getQuestionText(questionId) {
    const questionMap = {
        'activities': 'Activities:',
        'feelings': 'Feelings:',
        'time_spent': 'Time Spent:',
        'description': 'Description:',
        'sounds': 'Sounds:',
        'favorite_thing': 'Favorite Thing:',
        'comfort': 'Comfort:',
        'whispers': 'Whispers:',
        'favorite_spot': 'Favorite Spot:',
        'celebration': 'Celebration:'
    };
    return questionMap[questionId] || 'Care:';
}

function completeReveal() {
    revealModal.classList.add('hidden');
    // Reset for next creature
    currentCreature = null;
    
    // Reset stages
    document.getElementById('silhouette-stage').classList.add('hidden');
    document.getElementById('creature-reveal-stage').classList.add('hidden');
    
    // Reset creature image
    const creatureImage = document.getElementById('creature-reveal-image');
    creatureImage.classList.remove('revealed');
    
    // Reset info
    document.getElementById('creature-reveal-info').classList.remove('revealed');
}

function showCreatureResult(creature) {
    const audioHTML = creature.audio_url ? `
        <div style="margin-bottom: 20px;">
            <h4><i class="fas fa-volume-up"></i> Creature Sound:</h4>
            <div style="background: rgba(78, 205, 196, 0.1); padding: 15px; border-radius: 10px; border-left: 3px solid #4ecdc4;">
                <p style="font-style: italic; color: #4ecdc4; margin-bottom: 10px;">"${creature.sound_text}"</p>
                <p style="font-size: 0.9rem; color: #888; margin-bottom: 10px;">Voice: ${creature.voice_description}</p>
                <button class="btn btn-secondary" onclick="playCreatureSound('${creature.audio_url}')" style="margin-right: 10px;">
                    <i class="fas fa-play"></i> Play Sound
                </button>
                <span style="font-size: 0.8rem; color: #888;">Sound: ${creature.sound_name}</span>
            </div>
        </div>
    ` : `
        <div style="margin-bottom: 20px;">
            <h4><i class="fas fa-volume-up"></i> Creature Sound:</h4>
            <div style="background: rgba(255, 107, 107, 0.1); padding: 15px; border-radius: 10px; border-left: 3px solid #ff6b6b;">
                <p style="font-style: italic; color: #ff6b6b;">"${creature.sound_text}"</p>
                <p style="font-size: 0.9rem; color: #888;">Voice: ${creature.voice_description}</p>
                <p style="font-size: 0.8rem; color: #888;">(Audio generation failed, but here's what your creature sounds like!)</p>
            </div>
        </div>
    `;

    creatureContent.innerHTML = `
        <h2 style="color: #ff6b6b; margin-bottom: 20px;">
            <i class="fas fa-dragon"></i> Your Creature Has Hatched!
        </h2>
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="${creature.image_url}" alt="Hatched Creature" style="max-width: 100%; border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
        </div>
        ${audioHTML}
        <div style="margin-bottom: 20px;">
            <h4>Care History:</h4>
            <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px;">
                <p><strong>Environment:</strong> ${creature.care_responses.environment}</p>
                <p><strong>Duration:</strong> ${creature.care_responses.duration}</p>
                <p><strong>Care:</strong> ${creature.care_responses.care}</p>
            </div>
        </div>
        <div style="text-align: center;">
            <button class="btn btn-primary" onclick="closeCreatureModal()">
                <i class="fas fa-heart"></i> Meet My Creature!
            </button>
        </div>
    `;
    
    creatureModal.classList.remove('hidden');
    
    // Auto-play the sound after a short delay
    if (creature.audio_url) {
        setTimeout(() => {
            playCreatureSound(creature.audio_url);
        }, 1000);
    }
}

function playCreatureSound(audioUrl) {
    try {
        const audio = new Audio(audioUrl);
        audio.play().catch(error => {
            console.log('Audio play failed:', error);
        });
    } catch (error) {
        console.log('Audio creation failed:', error);
    }
}

function closeCreatureModal() {
    creatureModal.classList.add('hidden');
    // Reset for next egg
    console.log('Resetting currentEgg to null in closeCreatureModal');
    currentEgg = null;
    careQuestions = null;
}

// Modal Close Events
closeModal.addEventListener('click', closeResultModal);
resultModal.addEventListener('click', (e) => {
    if (e.target === resultModal) {
        closeResultModal();
    }
});

// Care modal close events
careModal.addEventListener('click', (e) => {
    if (e.target === careModal) {
        console.log('Care modal closed by clicking outside, currentEgg:', currentEgg);
        careModal.classList.add('hidden');
    }
});

// Creature modal close events
creatureModal.addEventListener('click', (e) => {
    if (e.target === creatureModal) {
        closeCreatureModal();
    }
});

// Reveal modal close events
revealModal.addEventListener('click', (e) => {
    if (e.target === revealModal) {
        completeReveal();
    }
});

// Image viewer modal close events
imageViewerModal.addEventListener('click', (e) => {
    if (e.target === imageViewerModal) {
        closeImageViewer();
    }
});

// Image viewer close button
imageViewerModal.querySelector('.close').addEventListener('click', closeImageViewer);

// File Upload Preview
document.getElementById('image-upload').addEventListener('change', (e) => {
    const file = e.target.files[0];
    const uploadText = document.getElementById('upload-text');
    const generateBtn = document.getElementById('generate-btn');
    
    if (file) {
        uploadText.textContent = file.name;
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-sparkles"></i> Generate Egg';
    } else {
        uploadText.textContent = 'Click to upload an image';
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-sparkles"></i> Generate Egg';
    }
});

// Debug function to check currentEgg state
window.debugCurrentEgg = function() {
    console.log('Current egg state:', currentEgg);
    console.log('Care questions state:', careQuestions);
    return { currentEgg, careQuestions };
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Disable generate button by default
    document.getElementById('generate-btn').disabled = true;
    
    // Load collection if on collection tab
    if (document.querySelector('[data-tab="collection"].active')) {
        loadCollection();
    }
    
    console.log('Page loaded, currentEgg:', currentEgg);
}); 