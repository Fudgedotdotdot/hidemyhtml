function parse() {
  return new Promise(function(resolve) {
    var tweets = document.getElementsByClassName('tweet');
    var encodedHTML = "";

    for (var i = 0; i < tweets.length; i++) {
      var tweet = tweets[i];
      var commentNodes = tweet.childNodes;
      for (var j = 0; j < commentNodes.length; j++) {
        var node = commentNodes[j];
        if (node.nodeType === Node.COMMENT_NODE) {
          encodedHTML = node.nodeValue.trim();
          break;
        }
      }
    }

    resolve(encodedHTML);
  });
}

function decode() {
  return parse().then(function (encodedHTML) {
    var KEY = "ENC_KEY";
    var decodedBase64 = atob(encodedHTML);
    var decodedArray = [];
    for (var i = 0; i < decodedBase64.length; i++) {
      decodedArray.push(decodedBase64.charCodeAt(i));
    }
    var compressed = new Uint8Array(decodedArray);

    var decrypted = new Uint8Array(compressed.length);
    for (var i = 0; i < compressed.length; i++) {
      decrypted[i] = compressed[i] ^ KEY.charCodeAt(i % KEY.length);
    }

    var stream = new ReadableStream({
      start: function(controller) {
        controller.enqueue(decrypted);
        controller.close();
      }
    });

    var decompressedStream = stream.pipeThrough(new DecompressionStream('gzip'));
    var reader = decompressedStream.getReader();

    var chunks = [];
    function readChunk() {
      return reader.read().then(function(result) {
        if (result.done) {
          var decompressed = new TextDecoder().decode(new Uint8Array(chunks.reduce(function(acc, chunk) {
            return acc.concat(Array.from(chunk));
          }, [])));
          return decompressed;
        }
        chunks.push(result.value);
        return readChunk();
      });
    }
    
    return readChunk();
  });
}

decode().then(function(result) {
  document.write(result);
});
