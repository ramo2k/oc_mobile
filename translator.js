let originalContent = {};

document.addEventListener("DOMContentLoaded", function() {
    const allTextNodes = getTextNodes(document.body);

    allTextNodes.forEach((node, index) => {
        const contentId = `content-id-${index}`;
        originalContent[contentId] = node.nodeValue;
        const spanNode = document.createElement('span');
        spanNode.setAttribute("data-content-id", contentId);
        spanNode.textContent = node.nodeValue;
        node.parentNode.replaceChild(spanNode, node);
    });
});

document.getElementById("lang-fr").addEventListener("click", function (event) {
    event.preventDefault();
    translateContent('fr');
});

document.getElementById("lang-en").addEventListener("click", function (event) {
    event.preventDefault();
    translateContent('en');
});

async function translateContent(targetLanguage) {
  const allSpanElements = document.querySelectorAll('span[data-content-id]');
  let allText = "";

  allSpanElements.forEach(spanElement => {
      const contentId = spanElement.getAttribute("data-content-id");
      const content = spanElement.textContent;

      if ((targetLanguage === 'fr' && content === originalContent[contentId]) ||
          (targetLanguage === 'en' && content !== originalContent[contentId])) {
          return;
      }

      allText += " " + content;
  });

  let translatedText = await translateUsingLibreTranslate(allText, targetLanguage);
  let translatedArray = translatedText.split(" ");

  allSpanElements.forEach(spanElement => {
      spanElement.textContent = translatedArray.shift();
  });
}

async function translateUsingLibreTranslate(text, targetLanguage) {
  const url = 'https://libretranslate.com/translate';
  const body = JSON.stringify({
      q: text,
      source: 'en',
      target: targetLanguage
  });

  try {
      const response = await fetch(url, {
          method: 'POST',
          body: body,
          headers: {'Content-Type': 'application/json'}
      });

      const data = await response.json();

      if (!response.ok) {
          // If we got a non-200 status code, let's log the text that caused the problem
          console.error(`HTTP error! status: ${response.status}, text: ${text}`);
          console.error('Response:', data);
          throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!data.translatedText) {
          console.error('No translatedText property in response:', data);
          return text;  // Return the original text if no translation was received
      }

      return data.translatedText;
  } catch (error) {
      console.error('Error during translation:', error);
      return text;  // Return the original text if an error occurred
  }
}





function getTextNodes(element) {
    const textNodes = [];
    const treeWalker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);

    let currentNode = treeWalker.nextNode();
    while (currentNode) {
        if (currentNode.parentNode.nodeName !== 'SCRIPT') {
            textNodes.push(currentNode);
        }
        currentNode = treeWalker.nextNode();
    }

    return textNodes;
}