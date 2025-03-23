# Quantum Cryptography Simulation

This repository simulates different cryptographic methods:

- No encryption
- BB84 Protocol
- Ekert Protocol

To get started with these simulations:
1. Clone the repository:
   ```
   git clone https://github.com/azimonti/quantum-cryptography-simulation.git
   ```
2. Navigate to the repository directory:
   ```
   cd quantum-cryptography-simulation
   ```
3. Install required dependencies (a virtual environment can be created running the script `create_env.sh`):
   ```
   pip install -r requirements.txt
   ```
4. Change `SECRET_KEY` in `config.json` (it is set as example for development purposes)
5 . Run the simulation scripts:
   ```
   python app.py
   ```

## Simulations

All the simulations rely on one-time pad cryptography, which is absolutely secured. Therefore the encrypted message is always broadcasted on a a public channel and Eve can capture it.

The difference is how the secret key is exchanged and what is the behavior when an eavesdropper is intercepting the key and what Alice and Bob do to ensure that the key is not leaked.

### No Protocol

In the case where no encryption protocol is used, there is no reconciliation between Bob and Alice, and if an eavesdropper is present, just hold a valid copy of the key and can decode the message without Alice or Bob noticing it.

## Contributing

Contributions to the Quantum Cryptography Simulation project are welcome. Whether it's through submitting bug reports, proposing new features, or contributing to the code, your help is appreciated. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or want to get in touch regarding the project, please open an issue or contact the repository maintainers directly through GitHub.

## TODO

- [x] Implement one-time pad cryptography ([#1](https://github.com/azimonti/quantum-cryptography-simulation/issues/1))
- [ ] Implement BB84 Protocol ([#2](https://github.com/azimonti/quantum-cryptography-simulation/issues/2))
- [ ] Implement Ekert Protocol ([#3](https://github.com/azimonti/quantum-cryptography-simulation/issues/3))
