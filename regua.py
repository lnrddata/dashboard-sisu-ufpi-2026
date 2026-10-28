"""Componente "Sua posição na cota": faixa de progresso com marcadores, selo de status e indicadores (HTML/CSS autônomo)."""

_CSS = """<style>
.rg{--azul:#1F5FBF;--navy:#0B1F3A;--voce:#0B1F3A;--ok:#12744D;--warn:#7A5200;--mudo:#5B6B82}   /* textos com contraste ≥ 4,5:1 */
.rg-top{display:flex;justify-content:space-between;align-items:flex-start;gap:10px 16px;flex-wrap:wrap}
.rg-h{font-size:1.15rem;font-weight:700;color:var(--navy)}
.rg-i{display:inline-block;margin-left:6px;width:17px;height:17px;line-height:16px;text-align:center;border:1.5px solid #5B6B82;
  border-radius:50%;font-size:.76rem;color:#5B6B82;cursor:help;vertical-align:middle}
.rg-s{color:#5B6B82;font-size:.88rem;margin:1px 0 0}
.rg-chip{display:inline-flex;align-items:center;gap:7px;padding:6px 14px;border-radius:999px;font-size:.85rem;font-weight:700;
  border:1px solid currentColor;background:color-mix(in srgb,currentColor 9%,white)}
.rg-chip::before{content:"";width:8px;height:8px;border-radius:50%;background:currentColor}
.rg-chip.ok{color:var(--ok)}.rg-chip.warn{color:var(--warn)}.rg-chip.mudo{color:var(--mudo)}
.rg-area.curta{height:122px}
.rg-area{position:relative;height:168px;margin:6px 22px 0;container-type:inline-size}
.rg-call{--W:96px;--l:clamp(0px,calc(var(--p)*1cqw - var(--W)/2),calc(100cqw - var(--W)));position:absolute;left:var(--l);width:var(--W);
  box-sizing:border-box;text-align:center;padding:5px 0;border-radius:999px;white-space:nowrap;font-size:.8rem;line-height:1.3;
  box-shadow:0 4px 12px -6px rgba(11,31,58,.45);animation:rgpill .5s ease both .5s}
.rg-call b{font-weight:800;margin-left:4px}
.rg-call::after{content:"";position:absolute;left:clamp(12px,calc(var(--p)*1cqw - var(--l)),calc(var(--W) - 12px));width:2px;
  transform:translateX(-50%);background:inherit}
.rg-you{top:6px;background:var(--voce);color:#fff;border:1.5px solid var(--voce)}
.rg-you::after{top:100%;height:32px}
.rg-ref{--W:176px;top:126px;background:#fff;color:var(--azul);border:1.5px solid var(--azul)}
.rg-ref::after{bottom:100%;height:32px;background:var(--azul)}
.rg-track{position:absolute;left:0;right:0;top:70px;height:20px;background:#E3EAF5;border-radius:10px;
  box-shadow:inset 0 1px 2px rgba(11,31,58,.12)}
.rg-tick{position:absolute;top:0;width:1px;height:20px;background:rgba(11,31,58,.10)}
.rg-fill{position:absolute;left:0;top:0;height:100%;width:var(--w);border-radius:10px;animation:rgw .9s cubic-bezier(.2,.8,.2,1) both;
  background:linear-gradient(90deg,#2E6FD9,#123D82)}
.rg-fill.proj{background:repeating-linear-gradient(135deg,#9DB9E8 0 6px,#B9CDEE 6px 12px)}
.rg-gap{position:absolute;top:0;height:100%;border-radius:0 10px 10px 0;animation:rgfade .6s ease both .7s;overflow:hidden;
  background:repeating-linear-gradient(135deg,rgba(242,177,0,.62) 0 5px,rgba(242,177,0,.28) 5px 10px);
  text-align:center;line-height:20px;font-size:.8rem;font-weight:800;color:#5C3D00;white-space:nowrap}
.rg-dot{position:absolute;top:80px;border-radius:50%;transform:translate(-50%,-50%);box-sizing:border-box;animation:rgpop .5s ease both .4s}
.rg-dot.ref{width:24px;height:24px;background:var(--azul);border:4px solid #fff;box-shadow:0 0 0 2px var(--azul),0 4px 10px -2px rgba(31,95,191,.6)}
.rg-dot.ref.proj{background:#fff;border:4px solid var(--azul);box-shadow:0 4px 10px -2px rgba(31,95,191,.4)}
.rg-dot.voce{width:30px;height:30px;background:var(--voce);border:4px solid #fff;box-shadow:0 0 0 1.5px var(--voce),0 4px 12px -2px rgba(11,31,58,.55)}
.rg-dot.voce::before{content:"";position:absolute;inset:-4px;border-radius:50%;border:2px solid var(--voce);animation:rgpulse 1.9s ease-out infinite}
.rg-tk{position:absolute;top:98px;transform:translateX(-50%);font-size:.8rem;color:#5B6B82;font-variant-numeric:tabular-nums;white-space:nowrap}
.rg-tk.ini{color:#0B1F3A;font-weight:700}
.rg-end{position:absolute;top:98px;font-size:.8rem;color:#5B6B82;font-variant-numeric:tabular-nums}
.rg-end b{color:var(--navy)}
.rg-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:4px}
.rg-st{position:relative;border-radius:12px;padding:11px 14px 10px 18px;background:#F6F8FC;border:1px solid #E6EAF1;overflow:hidden}
.rg-st::before{content:"";position:absolute;left:0;top:0;bottom:0;width:5px;background:var(--c)}
.rg-st .l{font-size:.76rem;color:#5B6B82;font-weight:700;text-transform:uppercase;letter-spacing:.03em}
.rg-st .v{font-size:1.7rem;font-weight:800;color:var(--navy);line-height:1.25;font-variant-numeric:tabular-nums}
.rg-st .u{font-size:.8rem;color:#5B6B82;min-height:1em}
@keyframes rgw{from{width:0}}
@keyframes rgfade{from{opacity:0}}
@keyframes rgpill{from{opacity:0;transform:translateY(6px)}}
@keyframes rgpop{from{opacity:0;transform:translate(-50%,-50%) scale(.6)}}
@keyframes rgpulse{0%{transform:scale(.85);opacity:.9}100%{transform:scale(1.9);opacity:0}}
@media (max-width:640px){.rg-call{font-size:.78rem;--W:88px}.rg-ref{--W:156px}.rg-area{margin:6px 14px 0}}
@media (prefers-reduced-motion:reduce){.rg *,.rg *::before{animation:none!important}}
</style>"""


def _pos(n: int) -> str:
    return f"{n} {'posição' if n == 1 else 'posições'}"


def _passo(fim: int) -> int:
    """Intervalo "redondo" entre as marcações da faixa (no máximo ~10 rótulos)."""
    return next((s for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500) if fim / s <= 10), 1000)


def regua_html(total: int, voce: int, pos_atual: int, ultimo, alcance, abertas) -> str:
    """Faixa da 1ª posição até a do candidato (ou até o ponto de corte, se ele estiver além): só o que importa, sem espremer o começo
    da fila numa lista longa. O tamanho da lista aparece num indicador à parte.
    voce: posição original; ultimo: último convocado da lista (ou None); alcance: até onde as vagas abertas chegam (usado quando ninguém
    da lista foi chamado); abertas: nº de vagas abertas. A etiqueta "Você" fica acima da faixa e a de referência abaixo."""
    real = ultimo is not None
    ref = ultimo if real else alcance
    fim = max(voce, ref or 0, 8)                       # a faixa termina na sua posição (mínimo de 8 posições para não ficar minúscula)
    pct = lambda x: (x - 1) / max(fim - 1, 1) * 100
    p_you, p_ref = pct(voce), (pct(ref) if ref else None)
    proj = "" if real else " proj"
    dist = None if ref is None else max(voce - ref, 0)

    # selo de status: resume a situação numa frase
    if ref is None:
        chip = ("mudo", "Sem vagas cadastradas nesta cota" if abertas is None else "Nenhuma vaga aberta nesta cota")
    elif dist == 0:
        chip = ("ok", "Sua posição está dentro do alcance da convocação" if real else "Sua posição está dentro das vagas abertas")
    else:
        chip = ("warn", f"{_pos(dist)} à frente da sua posição" if real else f"{_pos(dist)} além das vagas abertas")

    call_ref = gap = dot_ref = ""
    if ref:
        rot, val = ("Último convocado", f"{ref}º") if real else ("Vagas abertas", f"até o {ref}º")
        call_ref = f'<div class="rg-call rg-ref" style="--p:{p_ref:.2f}">{rot}<b>{val}</b></div>'
        dot_ref = f'<span class="rg-dot ref{proj}" style="left:{p_ref:.2f}%"></span>'
        if voce > ref:
            larg = p_you - p_ref
            gap = (f'<div class="rg-gap" style="left:{p_ref:.2f}%;width:{larg:.2f}%">' + (_pos(dist) if larg >= 24 else "") + '</div>')

    # uma marcação por posição "redonda"; o rótulo some perto do ponto de corte para não cruzar o conector da etiqueta
    s = _passo(fim)
    marcas = [k for k in range(s, fim + 1, s)]
    ticks = "".join(f'<i class="rg-tick" style="left:{pct(k):.2f}%"></i>' for k in marcas if 1 < k < fim)
    rotulos = "".join(f'<span class="rg-tk" style="left:{pct(k):.2f}%">{k}º</span>' for k in marcas
                      if k != 1 and abs(pct(k) - p_you) >= 4 and (p_ref is None or abs(pct(k) - p_ref) >= 6))
    if p_you >= 4 and (p_ref is None or p_ref >= 6):
        rotulos += '<span class="rg-tk ini" style="left:0">1º</span>'

    c = lambda cor, l, v, u="": f'<div class="rg-st" style="--c:{cor}"><div class="l">{l}</div><div class="v">{v}</div><div class="u">{u}</div></div>'
    stats = (c("#1F5FBF", "Sua posição", f"{voce}º", f"posição atual: {pos_atual}º" if pos_atual != voce else "na lista de espera")
             + c("#5B6B82", "Total na cota", fi_br(total), "candidatos na lista")
             + c("#7A8799", "Último convocado", f"{ultimo}º" if real else "—", "" if real else "ninguém da lista chamado ainda")
             + c("#F2B100", "Distância", "—" if dist is None else str(dist), "" if dist is None else ("posição" if dist == 1 else "posições"))
             + c("#8FB0E8", "Vagas abertas", "n/d" if abertas is None else str(abertas)))

    return (_CSS + '<div class="rg"><div class="rg-top"><div><div class="rg-h">Sua posição na cota<span class="rg-i" title="Posição na classificação '
            'da sua cota. O marcador azul mostra até onde a convocação já chegou (ou até onde as vagas abertas chegariam).">i</span></div>'
            '<div class="rg-s">A faixa vai da 1ª posição até a sua e mostra até onde a convocação já chegou.</div></div>'
            f'<span class="rg-chip {chip[0]}">{chip[1]}</span></div>'
            f'<div class="rg-area{"" if ref else " curta"}"><div class="rg-call rg-you" style="--p:{p_you:.2f}">Você<b>{voce}º</b></div>'
            f'<div class="rg-track">{ticks}<div class="rg-fill{proj}" style="--w:{p_ref or 0:.2f}%"></div>{gap}</div>'
            f'{dot_ref}<span class="rg-dot voce" style="left:{p_you:.2f}%"></span>{rotulos}{call_ref}</div>'
            f'<div class="rg-stats">{stats}</div></div>')


def fi_br(n) -> str:
    """Inteiro com separador de milhar no padrão brasileiro (1.234)."""
    return f"{int(n):,}".replace(",", ".")
