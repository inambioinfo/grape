#!/usr/bin/env python
"""Grape basic tools and utilities
and manage modules
"""
import jip
from jip import tool, pipeline
from .buildout import module

R = jip.templates.render_template

def bin_path(module, bin=''):
    """ Return the absolute path of a module binary """
    import os
    module_path = module._load_modules()[0]
    path = os.path.join(module_path, 'bin', bin)
    return path


@module([("gemtools", "1.6.2")])
@tool('grape_gem_index')
class GemIndex(object):
    """\
    The GEM Indexer tool

    Usage:
        gem_index -i <genome> [-o <genome_index>] [--no-hash]

    Options:
        --help  Show this help message
        -o, --output <genome_index>  The output GEM index file [default: ${input|ext}.gem]
        --no-hash  Do not produce the hash file [default: false]

    Inputs:
        -i, --input <genome>  The fasta file for the genome
    """
    def setup(self):
        self.name('index.${input|name|ext}')
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-t')

    def get_command(self):
        return "bash", "%s ${options()}" % bin_path(self, 'gemtools index')


@module([("gemtools", "1.6.2")])
@tool('grape_gem_t_index')
class GemTranscriptomeIndex(object):
    """\
    The GEM Transcrptome Indexer tool

    Usage:
        gem_t_index -i <genome_index> -a <annotation> [-m <max_read_length>] [-o <output_prefix>]

    Options:
        --help  Show this help message
        -o, --output-prefix <output_dir>  The prefix for the output files (can contain a path) [default: ${annotation|abs|parent}/${annotation}]
        -m, --max-length <max_read_length>  Maximum read length [default: 150]

    Inputs:
        -i, --index <genome_index>  The GEM index file for the genome
        -a, --annotation <annotation>  The reference annotation in GTF format
    """
    def init(self):
        self.add_output('gem', "${output_prefix}.junctions.gem")
        self.add_output('keys', "${output_prefix}.junctions.keys")
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-t')

    def setup(self):
        self.name('t_index.${index|name|ext}')

    def get_command(self):
        return 'bash', '%s ${options()}' % bin_path(self, 'gemtools t-index')


@module([("gemtools", "1.6.2")])
@tool('grape_gem_rnatool')
class Gem(object):
    """\
    The GEMtools RNAseq Mapping Pipeline

    Usage:
        gem -f <fastq_file> -i <genome_index> -r <transcript_index> -q <quality> [-n <name>] [-o <output_dir>] [--single-end] [--no-bam] [--no-stats]

    Options:
        --help  Show this help message
        -q, --quality <quality>  The fastq offset quality
        -n, --name <name>  The output prefix name [default: ${fastq|name|ext|ext|re("[_-][12]","")}]
        -o, --output-dir <output_dir>  The output folder
        -s, --single-end    Run the single-end pipeline
        --no-bam  Do not generate the BAM file
        --no-stats  Do not generate mapping statistics

    Inputs:
        -f, --fastq <fastq_file>  The input fastq
        -i, --index <genome_index>  The GEM index file for the genome
        -r, --transcript-index <trascript_index>  The GEM index file for the transcriptome
    """
    def init(self):
        self.add_output('map', "${output_dir}/${name}.map.gz")

    def setup(self):
        self.name("gem.${name}")
        if not self.options['no_bam']:
            self.add_output('bam', "${output_dir}/${name}.bam")
            self.add_output('bai', "${output_dir}/${name}.bam.bai")
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-t')

    def get_command(self):
        from grape import Grape
        return 'bash', '%s ${options()}' % bin_path(self, 'gemtools rna-pipeline')


@module([("crgtools","0.1")])
@tool('grape_gem_quality')
class GemQuality(object):
    """\
    The GEMtools quality filter program

    Usage:
        gem.quality -i <input> -o <output> [-n name]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: stdout]

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
    """
    def setup(self):
        if self.options['name']:
            self.name("gem.quality.${name}")
            self.options['name'].hidden = True
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-t')

    def get_command(self):
        return 'bash', '%s ${options()}' % bin_path(self, 'gt.quality')


@module([("crgtools","0.1")])
@tool('grape_gem_filter')
class GemFilter(object):
    """\
    The GEMtools general filter program

    Usage:
        gem.filter -i <input> -o <output> [-n name] [--max-levenshtein-error <error>] [--max-matches <matches>]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: stdout]
        --max-levenshtein-error <error>  The maximum number of edit operations allowed
        --max-matches <matches>  The maximum number of matches allowed

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
    """
    def setup(self):
        if self.options['name']:
            self.name("gem.filter.${name}")
            self.options['name'].hidden = True
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-t')

    def get_command(self):
        return 'bash', '%s ${options()}' % bin_path(self, 'gt.filter')


@module([("gemtools", "1.6.2")])
@tool('grape_gem_stats')
class GemStats(object):
    """\
    The GEMtools stats program

    Usage:
        gem.stats -i <input> [-a] [-p] [-n name]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name
        -a, --all-tests  Perform all tests
        -p, --paired-end  Use paired-end information

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
    """
    def setup(self):
        if self.options['name'].value:
            self.name("gem.stats.${name}")
            self.options['name'].hidden = True
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-t')

    def get_command(self):
        return 'bash', '%s ${options()}' % bin_path(self, 'gt.stats')


@module([("gemtools", "1.6.2")])
@tool('grape_gem_sam')
class GemSam(object):
    """\
    The GEMtools SAM conversion program

    Usage:
        gem.sam -f <input> -o <output> -i <genome_index> -q <quality> [-l] [--read-group <read_group>] [--expect-single-end-reads] [--expect-paired-end-reads] [-n name]

    Options:
        --help  Show this help message
        -o, --output <output>  The output file [default: stdout]
        -n, --name <name>  The output prefix name
        -i, --index <genome_index>  The gem index for the genome
        -q, --quality <quality>  The quality offset
        -l, --sequence-lengths  Add sequence length to SAM header
        --read-group <read_group>  Add read group information
        --expect-single-end-reads  Override automatic SE/PE detection
        --expect-paired-end-reads  Override automatic SE/PE detection
    Inputs:
        -f, --input <input>  The input map file [default: stdin]
    """
    def setup(self):
        if self.options['name'].value:
            self.name("gem.sam.${name}")
            self.options['name'].hidden = True
        self.options['index'].short = '-I'
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-T')
        try:
            int(self.options['quality'].raw())
            self.options['quality'] = 'offset-%s' % self.options['quality'].raw()
        except:
            pass

    def get_command(self):
        return 'bash', '%s ${options()}' % bin_path(self, 'gem-2-sam')


@module([("crgtools", "0.1")])
@tool('grape_pigz')
class Pigz(object):
    """\
    The parallel gzip program

    Usage:
        pigz -i <input> -o <output> [-d] [-n name]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: stdout]
        -d, --decompress  Decompress

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
    """
    def setup(self):
        if self.options['name']:
            self.name("pigz.${name}")
            self.options['name'].hidden = True
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-p')

    def get_command(self):
        return 'bash', '%s ${threads|arg|suf(" ")}${decompress|arg|suf(" ")}${input|arg("-c ")|suf(" ")}${output|arg("> ")}' % bin_path(self, 'pigz')


@module([("crgtools", "0.1")])
@tool('grape_fix_se')
class AwkFixSE(object):
    """\
    An AWK script to fix SAM flags for single-end data

    Usage:
        fix_se -i <input> -o <output> [-n <name>]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: stdout]

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
    """
    def setup(self):
        if self.options['name']:
            self.name("awk_fix_se.${name}")
            self.options['name'].hidden = True

    def get_command(self):
        command = "\'BEGIN{OFS=FS=\"\\t\"}$0!~/^@/{split(\"1_2_8_32_64_128\",a,\"_\");for(i in a){if(and($2,a[i])>0){$2=xor($2,a[i])}}}{print}\'"
        return 'bash', 'awk %s ${input|arg("")|suf(" ")}${output|arg("> ")}' % command


@module([("crgtools", "0.1")])
@tool('grape_reverse_mate')
class AwkReverseMate(object):
    """\
    An AWK script for stranded data to reverse a mate in a SAM file.

    Usage:
        reverse_mate -i <input> -o <output> [-n <name>] [--second-mate]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: stdout]
        --second-mate  Reverse the second mate. [default: false]

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
    """
    def setup(self):
        if self.options['name']:
            self.name("awk_reverse_mate.${name}")
            self.options['name'].hidden = True
        self.add_option('mate', '128' if self.options['second_mate'] else '64')

    def get_command(self):
        command = "\'BEGIN {OFS=\"\\t\"} {if ($1!~/^@/ && and($2,${mate})>0) {$2=xor($2,0x10)}; print}\'"
        return 'bash', 'awk %s ${input|arg("")|suf(" ")}${output|arg("> ")}' % command


@module([("bedtools", "2.17.0")])
@tool('grape_bedtools_genome_cov')
class BedtoolsGenomeCov(object):
    """\
    The BEDtools genomeCoverage program

    Usage:
        bed.gencov -i <input> -o <output> [-s <strand>] [--bam] [-b] [--split] [-n <name>]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: stdout]
        -b, --bed-graph  Report depth in BedGraph format
        -s, --strand <strand>  Calculate coverage of intervals from a specific strand
        --split  Treat "split" BAM or BED12 entries as distinct BED intervals
        --bam  Input is in BAM format

    Inputs:
        -i, --input <input>  The input map file [default: stdin]

    """

    def setup(self):
        if self.options['name']:
            self.name("bed.gencov.${name}")
            self.options['name'].hidden = True
        if self.options['bam']:
            self.options['input'].short = '-ibam'
        self.options['bed_graph'].short = "-bg"
        self.options['split'].short = "-split"
        self.options['strand'].short = "-strand"

    def get_command(self):
        return 'bash', '%s ${bed_graph|arg|suf(" ")}${split|arg|suf(" ")}${strand|arg|suf(" ")}${input|arg|else(input.short+" stdin")|suf(" ")}${output|arg("> ")}' % bin_path(self, 'genomeCoverageBed')


@module([("bedtools", "2.17.0")])
@tool('grape_bedtools_bedgraph_bigwig')
class BedtoolsBedgraphBigwig(object):
    """\
    The BEDtools bedGraphToBigWig program

    Usage:
        bed.bgtobw -i <input> -o <output> -g <genome_fai> [-n <name>]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: stdout]

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
        -g, --genome <genome_fai>  The genome chromosme sizes

    """

    def setup(self):
        if self.options['name']:
            self.name("bed.bgtobw.${name}")
            self.options['name'].hidden = True

    def get_command(self):
        return 'bash', '%s ${input|arg("")|else("-")|suf(" ")}${genome|arg("")|suf(" ")}${output|arg("")}' % bin_path(self, 'bedGraphToBigWig')


@module([("samtools", "0.1.19")])
@tool('grape_samtools_view')
class SamtoolsView(object):
    """\
    The SAMtools view program

    Usage:
        sam.view -i <input> -o <output> [-s] [-b] [-n <name>]

    Options:
        --help  Show this help message
        -s, --input-sam  Read input in SAM format
        -b, --output-bam  Output BAM format
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: stdout]

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
    """
    def setup(self):
        if self.options['name']:
            self.name("sam.view.${name}")
            self.options['name'].hidden = True
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-@')
        self.options['input_sam'].short = "-S"

    def get_command(self):
        return 'bash', '%s ${input_sam|arg|suf(" ")}${output_bam|arg|suf(" ")}${threads|arg|suf(" ")}${input|arg("")|else("-")|suf(" ")}${output|arg("> ")}' % bin_path(self, 'samtools view')


@module([("samtools", "0.1.19")])
@tool('grape_samtools_sort')
class SamtoolsSort(object):
    """\
    The SAMtools sort program

    Usage:
        sam.sort -i <input> -o <output> [-m <max_memory>] [-n <name>]

    Options:
        --help  Show this help message
        -m, --max-memory <max_memory>  The maximum amount of RAM to use for sorting (per thread)
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: ${input|ext}_sorted.bam]

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
    """
    def setup(self):
        if self.options['name']:
            self.name("sam.sort.${name}")
            self.options['name'].hidden = True
        self.add_option('threads', '${JIP_THREADS}', hidden=False, short='-@')

    def get_command(self):
        return 'bash', '%s ${threads|arg|suf(" ")}${max_memory|arg|suf(" ")}${input|arg("")|else("-")|suf(" ")}${output|arg("")|ext}' % bin_path(self, 'samtools sort')


@module([("samtools", "0.1.19")])
@tool('grape_samtools_index')
class SamtoolsIndex(object):
    """\
    The SAMtools index program

    Usage:
        sam.index -i <input> -o <output> [-n <name>]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name
        -o, --output <output>  The output file [default: ${input|abs}.bai]

    Inputs:
        -i, --input <input>  The input map file
    """
    def setup(self):
        if self.options['name']:
            self.name("sam.index.${name}")
            self.options['name'].hidden = True


    def get_command(self):
        return 'bash', '%s ${input|arg("")|suf(" ")}${output|arg("")}' % bin_path(self, 'samtools index')


@module([("flux", "1.2.4")])
@tool('grape_flux')
class Flux(object):
    """\
    The Flux Capacitor tool

    Usage:
        flux -i <input> -a <annotation> [-o <output_dir>] [-n <name>]

    Options:
        --help  Show this help message
        -o, --output-dir <output_dir>  The output folder [default: ${input|parent}]
        -n, --name <name>  The output prefix name

    Inputs:
        -i, --input <input>  The input file with mappings
        -a, --annotation <annotation>  The reference annotation in GTF format
    """
    def init(self):
        self.add_output('output', "${output_dir|abs}/${name}.gtf", hidden=False, long='--output', short='-o')

    def setup(self):
        self.name("flux.${name}")
        self.options['output_dir'].hidden = True
        self.options['name'].hidden = True

    def get_command(self):
        return 'bash', '%s ${options()}' % bin_path(self, 'flux-capacitor')


@module([("crgtools", "0.1")])
@tool('grape_flux_split_features')
class AwkSplitFeatures(object):
    """\
    An AWK script to split the Flux Capacitor output by features

    Usage:
        split_features -i <input> [-n <name>]

    Options:
        --help  Show this help message
        -n, --name <name>  The output prefix name

    Inputs:
        -i, --input <input>  The input map file [default: stdin]
    """
    def init(self):
        self.add_output('transcript', '${input}.transcript.gtf')
        self.add_output('junction', '${input}.junction.gtf')
        self.add_output('intron', '${input}.intron.gtf')

    def setup(self):
        if self.options['name']:
            self.name("awk_split_flux_features.${name}")
            self.options['name'].hidden = True

    def get_command(self):
        command = "\'BEGIN{OFS=FS=\"\\t\"}{print > input\".\"$3\".gtf\"}\'"
        return 'bash', 'awk -v input=${input|arg("")|suf(" ")|ext} %s ${input|arg("")|suf(" ")}' % command


@pipeline('grape_gem_setup')
class SetupPipeline(object):
    """\
    The GEM indexes setup pipeline

    usage:
        setup -i <genome> -a <annotation> [-o <output_prefix>]

    Options:
        -i, --input <genome>              The input reference genome
        -a, --annotation <annotation      The input reference annotation
        -o, --output-dir <output_dir>     The output prefix

    """
    def init(self):
        self.add_output('index', '')
        self.add_output('t_out', '')
        self.add_output('t_index', '')

    def setup(self):
        self.name('gem.setup')
        out = self.output_dir
        if not out:
            index = "${input|ext}.gem"
            t_out = "${annotation}"
        else:
            index = "%s/${input|name|ext}.gem" % out
            t_out = "%s/${annotation|name}" % out
        self.options['index'] = index
        self.options['t_out'] = t_out
        self.options['t_index'] = t_out+'.gem'

    def pipeline(self):
        p = Pipeline()
        index = p.run('grape_gem_index', input=self.input, output=self.index)
        p.run('grape_gem_t_index', index=index, annotation=self.annotation, output_prefix=self.t_out)
        return p


@pipeline('grape_gem_rnapipeline')
class GrapePipeline(object):
    """\
    The default GRAPE RNAseq pipeline

    usage:
        rnaseq -f <fastq_file> -q <quality> -g <genome> -a <annotation> [-o <output_dir>] [--single-end] [--max-mismatches <mismatches>] [--max-matches <matches>]

    Inputs:
        -f, --fastq <fastq_file>        The input reference genome
        -g, --genome <genome_index>      The input reference genome
        -a, --annotation <annotation    The input reference annotation

    Options:
        -q, --quality <quality>         The fastq offset quality [default: 33]
        -s, --single-end                Run the single-end pipeline
        -m, --max-mismatches <mismatches>  The maximum number of mismatches allowed
        -n, --max-matches <matches>  The maximum number of matches allowed (multimaps)
        -o, --output-dir <output_dir>   The output prefix [default: ${fastq|abs|parent}]
    """
    def setup(self):
        self.name('gem.pipeline')
        self.add_option('sample','${fastq|name|ext|ext|re("[_-][12]","")}')

    def pipeline(self):
        p = Pipeline()
        gem_setup = p.run('grape_gem_setup', input=self.genome, annotation=self.annotation)
        gem = p.run('grape_gem_rnatool', index=gem_setup.index, transcript_index=gem_setup.t_index, single_end=self.single_end, fastq=self.fastq, quality=self.quality, no_bam=True, no_stats=True, output_dir=self.output_dir)
        sample = self.sample
        gem_filter = p.run('grape_gem_filter_p', input=gem.map, max_mismatches=self.max_mismatches, max_matches=self.max_matches, name=sample)
        gem_bam = p.run('grape_gem_bam_p', input=gem_filter.output, index=gem_setup.index, quality=self.quality, single_end=self.single_end, sequence_lengths=True, name=sample)
        flux = p.run('grape_flux', input=gem_bam.bam, annotation=self.annotation, output_dir=self.output_dir, name=sample)
        p.run('grape_flux_split_features', input=flux.output, name=sample)
        return p


@pipeline('grape_gem_filter_p')
class FilterPipeline(object):
    """\
    The GEM filter pipeline

    usage:
         gem.filter.pipeline -i <map_file> --max-mismatches <mismatches> --max-matches <matches> -o <output> [-l <name>]

    Inputs:
        -i, --input <map_file>        The input MAP file

    Options:
        -l, --name <name>  Prefix name
        -o, --output <output>  The output file [default: ${input|ext|ext}_m${max_mismatches}_n${max_matches}.map.gz]
        -m, --max-mismatches <mismatches>  The maximum number of edit operations allowed
        -n, --max-matches <matches>  The maximum number of matches allowed

    """
    def setup(self):
        self.name('gem.filter.pipeline')

    def pipeline(self):
        p = Pipeline()
        sample=self.options['name']
        gem_filter = p.run('grape_gem_quality', input=self.input, name=sample) | \
        p.run('grape_gem_filter', max_levenshtein_error=self.max_mismatches, name=sample) | \
        p.run('grape_gem_filter', max_matches=self.max_matches, name=sample) | \
        p.run('grape_pigz', output=self.output, name=sample)
        return p

@pipeline('grape_gem_bam_p')
class Gem2BamPipeline(object):
    """\
    The GEM to BAM conversion pipeline

    usage:
         gem2bam.pipeline -f <map_file> -i <gem_index> -q quality -o <output> [-s] [-l] [--read-group <read_group>] [-n <name>]

    Inputs:
        -f, --input <map_file>        The input MAP file
        -i, --index <gem_index>        The gem index for the genome

    Options:
        -n, --name <name>  Prefix name
        -s, --single-end  Expect single end input
        -q, --quality <quality>  The quality offset
        -l, --sequence-lengths  Add sequence lengths information to SAM header
        -o, --output <output>  The output file [default: ${input|ext|ext}.bam]
    """
    def init(self):
        self.add_output('bam', '${output}')
        self.add_output('bai', '${output}.bai')

    def setup(self):
        self.name('gem.to.bam.pipeline')

    def pipeline(self):
        p = Pipeline()
        sample=self.options['name']
        gem_bam = p.run('grape_pigz', input=self.input, decompress=True, name=sample) | \
        p.run('grape_gem_sam', index=self.index, read_group=self.read_group, quality=self.quality, sequence_lengths=self.sequence_lengths, expect_paired_end_reads=not self.single_end, expect_single_end_reads=self.single_end, name=sample) | \
        p.run('grape_samtools_view', input_sam=True, output_bam=True, name=sample) | \
        p.run('grape_samtools_sort', output=self.output, name=sample)
        gem_bai = p.run('grape_samtools_index', input=gem_bam.output, name=sample)
        return p


@pipeline('grape_bigwig')
class BigwigPipeline(object):
    """\
    The Bigwig pipeline

    usage:
         grape.bigwig -i <bam_file> -o <bw_file> -g <genome_file> [--stranded] [ --reverse-first-mate | --reverse-second-mate ]

    Inputs:
        -i, --input <bam_file>        The input MAP file
        -g, --genome <genome_file>    The genome chromosome sizes file

    Options:
        -n, --name <name>  Prefix name
        -o, --output <bw_file>  The output file [default: ${input|ext}.bw
        --stranded  Whether the data is stranded
        --reverse-first-mate  Reverse the first mate in the bam file
        --reverse-second-mate  Reverse the second mate in the bam file
    """
    def setup(self):
        self.name('bigwig.pipeline')

    def pipeline(self):
        p = Pipeline()
        sample=self.options['name']
        inp = self.input
        bam = self.input
        strands = {'-':'minusRaw','+':'plusRaw'}
        if self.options['reverse_first_mate']:
            bam = p.run('grape_samtools_view', input=bam, name=sample) | \
                  p.run('grape_reverse_mate', input=self.input, name=sample) | \
                  p.run('grape_samtools_view', input_sam=True, output_bam=True, name=sample)
        if self.options['reverse_second_mate']:
            bam = p.run('grape_samtools_view', input=bam, name=sample) | \
                  p.run('grape_reverse_mate', input=self.input, name=sample, second_mate=True) | \
                  p.run('grape_samtools_view', input_sam=True, output_bam=True, name=sample)
        print strands['-']
        bedgraph = p.job(temp=True).run('grape_bedtools_genome_cov', input=bam, output="${inp|ext}_${strands.get(strand.raw())}.bedgraph", bam=True, split=True, bed_graph=True, strand = "" if not self.stranded else ["+", "-"])
        p.run('grape_bedtools_bedgraph_bigwig', input=bedgraph.output, genome=self.genome, output='${input|ext}.bw')
        p.context(locals())
        return p
