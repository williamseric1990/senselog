#!/bin/bash
forever start -l senselog.log --append -e senselog.err senselog.js
