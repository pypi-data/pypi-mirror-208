"use strict";

class DecimalMask {
  constructor(input, options) {
    if (input instanceof HTMLInputElement === false) {
      throw new TypeError("The input should be a HTMLInputElement");
    }
    this.input = input;
    this.input.mask = this;

    this.opts = {
      keyEvent: "input",
      backspace: !this.input.required,
      format: {
        style: "decimal",
      },
    };
    this.opts = Object.assign(this.opts, options);

    this.changeInput();

    if (this.input.defaultValue) {
      const fixedValue = Number(this.input.value).toFixed(
        this.opts.decimalPlaces
      );
      this.input.value = this.masking(fixedValue);
    }

    this.input.addEventListener(
      this.opts.keyEvent,
      this.handleEvent.bind(this)
    );
    this.input.addEventListener("click", this.handleEvent.bind(this));
    this.input.addEventListener("dblclick", this.handleEvent.bind(this));
  }

  handleEvent(event) {
    if (event.type === "dblclick") {
      this.onDblclick();
    } else if (event.type === "click") {
      this.onClick(event);
    } else {
      this.onMasking(event);
    }
  }

  onDblclick() {
    this.input.setSelectionRange(0, this.input.value.length);
  }

  onClick() {
    const pos = DecimalMask.position(this.input.value);
    this.input.focus();
    this.input.setSelectionRange(pos, pos);
  }

  onMasking(event) {
    const onlyZeros = Number(DecimalMask.unmask(this.input.value)) === 0;
    if (
      this.opts.backspace &&
      event?.inputType === "deleteContentBackward" &&
      onlyZeros
    ) {
      this.input.value = "";
      return;
    }

    this.input.value = this.masking(this.input.value);
    const pos = DecimalMask.position(this.input.value);
    this.input.setSelectionRange(pos, pos);
  }

  changeInput() {
    this.input.setAttribute("type", "tel");
  }

  transformToDecimal(v) {
    const n = DecimalMask.unmask(v);
    const t = n.padStart(this.opts.decimalPlaces + 1, "0");
    const d = t.slice(-this.opts.decimalPlaces);
    const i = t.slice(0, t.length - this.opts.decimalPlaces);

    return `${i}.${d}`;
  }

  masking(value) {
    let opts = {
      minimumFractionDigits: this.opts.decimalPlaces,
    };
    opts = Object.assign(opts, this.opts.format);

    if (typeof value === "number") {
      value = value.toFixed(2);
    }

    let decimal = this.transformToDecimal(value);

    if (opts.style === "percent") {
      decimal = Number(decimal) / 100;

      if (decimal > 1) {
        decimal = 1;
      }
    }

    const r = new Intl.NumberFormat(this.opts.locales, opts).format(decimal);
    return r;
  }

  get value() {
    return Number(this.transformToDecimal(this.input.value));
  }

  set value(value) {
    this.input.value = this.masking(value);
  }

  static unmask(v) {
    return String(v).replace(/\D/g, "").replace(/^0+/g, "");
  }

  static position(v) {
    const nums = new Set(["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]);

    let cc = 0;
    for (let i = v.length - 1; i >= 0; i--) {
      if (nums.has(v[i])) {
        break;
      }
      cc++;
    }

    return String(v).length - cc;
  }
}
