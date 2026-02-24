import { H, Component, State } from '@stencil/core';

@Component({
  tag: 'a2ui-client',
  styleUrl: 'client.css',
  shadow: true
})
export class A2uiClient {
  @State() surfaceId: string = '';
  @State() title: string = '';
  @State() summary: string = '';
  @State() bullets: string[] = [];
  @State() isRendering: boolean = false;
  @State() error: string = '';
  @State() isLoading: boolean = false;

  private controller: AbortController | null = null;
  private eventSource: EventSource | null = null;

  async handleQuery() {
    this.isLoading = true;
    this.error = '';
    this.surfaceId = '';
    this.title = '';
    this.summary = '';
    this.bullets = [];
    this.isRendering = false;

    if (this.controller) {
      this.controller.abort();
    }
    this.controller = new AbortController();

    try {
      const response = await fetch(`/a2ui?q=${encodeURIComponent(this.queryInput)}`, {
        signal: this.controller.signal
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }

      await this.processStream(response.body as ReadableStream<Uint8Array>);

    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        this.error = error.message;
      }
    } finally {
      this.isLoading = false;
    }
  }

  async processStream(stream: ReadableStream<Uint8Array>) {
    const reader = stream.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const message = JSON.parse(line);
            await this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing JSONL line:', line, error);
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async handleMessage(message: any) {
    if (message.surfaceUpdate) {
      const surface = message.surfaceUpdate;
      this.surfaceId = surface.surfaceId;

      if (surface.components) {
        const titleComponent = surface.components.find((c: any) => c.id === 'title');
        const summaryComponent = surface.components.find((c: any) => c.id === 'summary');
        const bulletsComponent = surface.components.find((c: any) => c.id === 'bullets');

        if (summaryComponent?.component?.Text?.text?.binding) {
          const binding = summaryComponent.component.Text.text.binding;
          if (binding.includes('/view/summary')) {
            this.summary = this.getDataModelValue(binding);
          }
          if (binding.includes('/view/title')) {
            this.title = this.getDataModelValue(binding);
          }
          if (binding.includes('/view/bullets')) {
            const index = parseInt(binding.split('/view/bullets/')[1]);
            if (!isNaN(index) && index < this.bullets.length) {
              this.bullets[index] = this.getDataModelValue(binding);
            }
          }
        }
      }
    } else if (message.dataModelUpdate) {
      const dataModel = message.dataModelUpdate;
      if (dataModel.set) {
        dataModel.set.forEach((update: any) => {
          if (update.path.includes('/view/title')) {
            this.title = update.valueString || '';
          } else if (update.path.includes('/view/summary')) {
            this.summary = update.valueString || '';
          } else if (update.path.includes('/view/bullets')) {
            const index = parseInt(update.path.split('/view/bullets/')[1]);
            if (!isNaN(index) && index >= 0 && index < this.bullets.length) {
              this.bullets[index] = update.valueString || '';
            } else if (index < 7) {
              while (this.bullets.length <= index) {
                this.bullets.push('');
              }
              this.bullets[index] = update.valueString || '';
            }
          }
        });
      }
    } else if (message.beginRendering) {
      this.isRendering = true;
    }
  }

  getDataModelValue(binding: string): string {
    if (binding === '/view/title') {
      return this.title;
    } else if (binding === '/view/summary') {
      return this.summary;
    } else if (binding.startsWith('/view/bullets/')) {
      const index = parseInt(binding.split('/view/bullets/')[1]);
      if (!isNaN(index) && index < this.bullets.length) {
        return this.bullets[index] || '';
      }
    }
    return '';
  }

  render() {
    return (
      <H class="surface-container">
        <div class="query-section">
          <div class="input-group">
            <input
              type="text"
              class="query-input"
              value={this.queryInput}
              onInput={(e) => this.queryInput = (e.target as HTMLInputElement).value}
              placeholder="Posez une question..."
              disabled={this.isLoading}
            />
            <button
              class="query-button"
              onClick={() => this.handleQuery()}
              disabled={this.isLoading}
            >
              {this.isLoading ? 'Recherche...' : 'Envoyer'}
            </button>
          </div>
        </div>

        {this.error && <div class="error-message">Erreur: {this.error}</div>}

        {!this.isRendering && this.isLoading && (
          <div class="loading">Génération en cours...</div>
        )}

        {this.isRendering && this.surfaceId && (
          <div class="surface-content">
            <h1 class="title">{this.title || 'Titre'}</h1>
            <p class="summary">{this.summary || 'Résumé en cours...'}</p>
            <div class="bullets">
              {this.bullets.map((bullet, index) => (
                <li class="bullet-item">
                  {bullet || `Point ${index + 1}`}
                </li>
              ))}
            </div>
          </div>
        )}
      </H>
    );
  }

  @State() queryInput: string = '';
}