const decisionTree = {
    question: "Is your character a scientist?",
    yes: {
        question: "Did they work in physics?",
        yes: {
            question: "Did they live in the 20th century?",
            yes: {
                question: "Did they work on relativity theory?",
                yes: "Albert Einstein",
                no: {
                    question: "Did they work on quantum mechanics?",
                    yes: "Niels Bohr",
                    no: "Richard Feynman"
                }
            },
            no: "Isaac Newton"
        },
        no: {
            question: "Did they work in biology?",
            yes: {
                question: "Are they known for evolution theory?",
                yes: "Charles Darwin",
                no: {
                    question: "Did they work with radiation?",
                    yes: "Marie Curie",
                    no: "Louis Pasteur"
                }
            },
            no: {
                question: "Did they work with computers?",
                yes: {
                    question: "Did they work on AI?",
                    yes: "Alan Turing",
                    no: "John von Neumann"
                },
                no: "Thomas Edison"
            }
        }
    },
    no: {
        question: "Is your character an artist?",
        yes: {
            question: "Did they work during the Renaissance?",
            yes: {
                question: "Did they paint the Mona Lisa?",
                yes: "Leonardo da Vinci",
                no: "Michelangelo"
            },
            no: {
                question: "Did they paint Starry Night?",
                yes: "Vincent van Gogh",
                no: "Pablo Picasso"
            }
        },
        no: {
            question: "Are they a mathematician or engineer?",
            yes: {
                question: "Did they work on computer programming?",
                yes: {
                    question: "Were they the first programmer?",
                    yes: "Ada Lovelace",
                    no: "Grace Hopper"
                },
                no: {
                    question: "Did they live in ancient times?",
                    yes: "Pythagoras",
                    no: "Katherine Johnson"
                }
            },
            no: {
                question: "Are they an inventor or architect?",
                yes: {
                    question: "Did they work with electricity?",
                    yes: {
                        question: "Did they work on AC current?",
                        yes: "Nikola Tesla",
                        no: "Alexander Graham Bell"
                    },
                    no: "Steve Jobs"
                },
                no: {
                    question: "Did they design modern buildings?",
                    yes: "Frank Lloyd Wright",
                    no: "Imhotep"
                }
            }
        }
    }
};

let currentNode = decisionTree;
let steps = 0;

const questionElement = document.getElementById('question');
const yesButton = document.getElementById('yes-btn');
const noButton = document.getElementById('no-btn');
const restartButton = document.getElementById('restart-btn');
const reloadButton = document.getElementById('reload-btn');
const stepsElement = document.getElementById('steps');

function updateQuestion(text) {
    questionElement.textContent = text;
}

function showResult(character) {
    questionElement.textContent = `Is it ${character}?`;
    yesButton.style.display = 'none';
    noButton.style.display = 'none';
    restartButton.style.display = 'block';
}

function restartGame() {
    currentNode = decisionTree;
    steps = 0;
    stepsElement.textContent = `Steps: ${steps}`;
    updateQuestion(currentNode.question);
    yesButton.style.display = 'inline-block';
    noButton.style.display = 'inline-block';
    restartButton.style.display = 'none';
}

function reloadGame() {
    window.location.reload();
}

function handleAnswer(answer) {
    steps++;
    stepsElement.textContent = `Steps: ${steps}`;
    
    const nextNode = currentNode[answer];
    if (typeof nextNode === 'string') {
        showResult(nextNode);
    } else {
        currentNode = nextNode;
        updateQuestion(currentNode.question);
    }
}

yesButton.addEventListener('click', () => handleAnswer('yes'));
noButton.addEventListener('click', () => handleAnswer('no'));
restartButton.addEventListener('click', restartGame);
reloadButton.addEventListener('click', reloadGame);

function getAllCharacters(tree) {
    const characters = [];
    
    function traverse(node) {
        if (typeof node === 'string') {
            characters.push(node);
        } else if (node.yes) {
            traverse(node.yes);
            traverse(node.no);
        }
    }
    
    traverse(tree);
    return characters;
}

function initializeModals() {
    const howToPlayModal = new bootstrap.Modal(document.getElementById('howToPlayModal'));
    const charactersModal = new bootstrap.Modal(document.getElementById('charactersModal'));
    document.getElementById('how-to-play-btn').addEventListener('click', () => howToPlayModal.show());
    document.getElementById('character-info-btn').addEventListener('click', () => charactersModal.show());
}

// Initialize the game
restartGame();
initializeModals();
