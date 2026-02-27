const https = require('https');
const fs = require('fs');
const path = require('path');

/**
 * Retrieves the API key based on the environment fallback logic.
 * 
 * Environment Variable Reading Logic:
 * 1. Checks the explicitly provided customKey argument.
 * 2. If missing, checks the `ARK_API_KEY` system environment variable.
 * 3. If missing, searches for a `.env` file in the following paths: `/.env`, `./.env` (Current Working Directory), and `<script_directory>/.env`.
 *    It parses the file for the `ARK_API_KEY=` pattern and extracts the value if found.
 * 4. Returns null if all attempts fail.
 * 
 * @param {string|null} customKey - The user-provided API key, if any.
 * @returns {string|null} The resolved API key or null.
 */
/**
 * Retrieves a value from environment or .env files.
 */
function getFromEnv(keyName) {
    if (process.env[keyName]) return process.env[keyName];

    const envPaths = ['/.env', '.env', path.join(process.cwd(), '.env'), path.join(__dirname, '.env')];
    for (const envPath of envPaths) {
        if (fs.existsSync(envPath)) {
            const content = fs.readFileSync(envPath, 'utf8');
            const lines = content.split('\n');
            for (const line of lines) {
                if (line.startsWith(`${keyName}=`)) {
                    let value = line.substring(keyName.length + 1).trim();
                    if (value.startsWith('"') || value.startsWith("'")) {
                        value = value.substring(1, value.length - 1);
                    }
                    return value;
                }
            }
        }
    }
    return null;
}

function getApiKey(customKey) {
    return customKey || getFromEnv('ARK_API_KEY');
}

function getModelId(customModel) {
    return customModel || getFromEnv('SEEDREAM_ENDPOINT_ID');
}

/**
 * Generates an image using the Volcengine Seedream API.
 * 
 * @param {Object} params - The inputs for the generation request.
 * @param {string} params.prompt - The text description of the image to generate. Required.
 * @param {string} [params.model] - The endpoint ID of the model. If missing, uses SEEDREAM_ENDPOINT_ID.
 * @param {string} [params.api_key] - Custom API key to use. Overrides environment variable.
 * @param {string} [params.size] - Target image size. Can be a resolution class (e.g., '2K', '3K') or explicit dimensions (e.g., '2048x2048').
 * @param {boolean} [params.watermark=false] - Whether to include an AI watermark.
 * @param {Object} [params.optimize_prompt_options] - Options to auto-optimize the prompt.
 * @param {Array} [params.tools] - A list of tools for the model to use (e.g., [{"type": "web_search"}]).
 * @param {string} [params.output_format] - Output image format (e.g., 'png', 'jpeg').
 * @param {string} [params.sequential_image_generation] - Sequential image generation strategy (e.g., 'auto').
 * @param {string} [params.download_dir] - Directory to save generated images.
 * 
 * @returns {Promise<Object>} A promise resolving to the API response object.
 * 
 * Return value format (on success):
 * {
 *   "data": [
 *     {
 *       "url": "https://...",
 *       "size": "2048x2048"
 *     }
 *   ],
 *   "input_params": { ... },
 *   "usage": { 
 *       "generated_images": 1,
 *       ...
 *   }
 * }
 * 
 * Return value format (on failure):
 * {
 *   "error": "<Error Details or HTTP Code>", 
 *   "message": "<Optional Server Message>" 
 * }
 */
async function generateImage(params) {
    const modelId = getModelId(params.model);
    if (!modelId) {
        return { error: "Require model or SEEDREAM_ENDPOINT_ID in .env/environment" };
    }

    const payload = {
        model: modelId,
        prompt: params.prompt,
        watermark: params.watermark !== undefined && params.watermark !== null ? params.watermark : false
    };

    if (params.size !== undefined && params.size !== null) {
        payload.size = params.size;
    }
    if (params.optimize_prompt_options !== undefined && params.optimize_prompt_options !== null) {
        payload.optimize_prompt_options = params.optimize_prompt_options;
    }
    if (params.tools !== undefined && params.tools !== null) {
        payload.tools = params.tools;
    }
    if (params.output_format !== undefined && params.output_format !== null) {
        payload.output_format = params.output_format;
    }
    if (params.sequential_image_generation !== undefined && params.sequential_image_generation !== null) {
        payload.sequential_image_generation = params.sequential_image_generation;
    }

    const downloadImage = (url, dest) => {
        return new Promise((resolve, reject) => {
            const file = fs.createWriteStream(dest);
            https.get(url, (response) => {
                response.pipe(file);
                file.on('finish', () => {
                    file.close(resolve);
                });
            }).on('error', (err) => {
                fs.unlink(dest, () => { });
                reject(err.message);
            });
        });
    };

    const dataString = JSON.stringify(payload);

    const options = {
        hostname: 'ark.cn-beijing.volces.com',
        port: 443,
        path: '/api/v3/images/generations',
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(dataString)
        }
    };

    return new Promise((resolve) => {
        const req = https.request(options, (res) => {
            let resData = '';
            res.on('data', (chunk) => resData += chunk);
            res.on('end', async () => {
                try {
                    const resJson = JSON.parse(resData);

                    if (resJson.data) {
                        resJson.input_params = payload;

                        if (params.download_dir) {
                            const saveDir = params.download_dir;
                            if (!fs.existsSync(saveDir)) {
                                fs.mkdirSync(saveDir, { recursive: true });
                            }

                            for (let i = 0; i < resJson.data.length; i++) {
                                const item = resJson.data[i];
                                if (item.url) {
                                    try {
                                        const ext = payload.output_format === 'png' ? '.png' : '.jpeg';
                                        const filename = `image_${resJson.created || Date.now()}_${i}${ext}`;
                                        const destPath = path.join(saveDir, filename);
                                        await downloadImage(item.url, destPath);
                                        item.local_path = destPath;
                                    } catch (err) {
                                        item.local_path_error = err;
                                    }
                                }
                            }
                        }
                    }
                    resolve(resJson);
                } catch (e) {
                    resolve({ error: "Parse error", message: resData });
                }
            });
        });

        req.on('error', (e) => resolve({ error: e.message }));
        req.write(dataString);
        req.end();
    });
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const params = {};
    for (let i = 0; i < args.length; i++) {
        if (args[i].startsWith('--')) {
            const key = args[i].substring(2);
            params[key] = args[i + 1];
            i++;
        }
    }

    if (params.watermark === "true") params.watermark = true;
    if (params.watermark === "false") params.watermark = false;

    if (params.optimize_prompt_options) {
        try {
            params.optimize_prompt_options = JSON.parse(params.optimize_prompt_options);
        } catch (e) {
            console.error("Error: --optimize_prompt_options must be a valid JSON string");
            process.exit(1);
        }
    }

    if (params.tools) {
        try {
            params.tools = JSON.parse(params.tools);
        } catch (e) {
            console.error("Error: --tools must be a valid JSON string");
            process.exit(1);
        }
    }

    if (!params.prompt) {
        console.error("Usage: node seedream.js --prompt <prompt> [--model <model>] [--api_key <key>] [--size <size>] [--watermark <true/false>] [--output_format <format>] [--sequential_image_generation <mode>] [--tools <json>] [--optimize_prompt_options <json>]");
        process.exit(1);
    }

    generateImage(params).then(res => console.log(JSON.stringify(res, null, 2)));
}

module.exports = { generateImage };
